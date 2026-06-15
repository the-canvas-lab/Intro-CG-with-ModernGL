# =============================================================================
# Exercise 037 — Flashlight
# =============================================================================
# A flashlight is a spot light that moves and rotates with the camera —
# it always illuminates exactly what the player is looking at.
#
# The scene and spot light shader are already set up.
#
# TODO 1 — In render(), make the spot light follow the camera by uploading
#           the right uniforms each frame.
#
# TODO 2 — Implement adjust_cone(delta) so ↑ / ↓ widens or narrows the beam.
#           The cone angle is stored in degrees; the shader expects cosines.
#           The outer cone is always 2.5° wider than the inner cone.
#
# Controls:  WASD — move   Mouse — look   ↑ / ↓ — widen / narrow beam   Esc — quit
# =============================================================================

import math
import os
import sys

import glm
import moderngl
import numpy as np
import pygame
import pywavefront

os.environ['SDL_WINDOWS_DPI_AWARENESS'] = 'permonitorv2'

pygame.init()
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
pygame.display.gl_set_attribute(
    pygame.GL_CONTEXT_PROFILE_MASK,
    pygame.GL_CONTEXT_PROFILE_CORE
)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)
pygame.display.set_mode((800, 600), flags=pygame.OPENGL | pygame.DOUBLEBUF, vsync=True)
pygame.display.set_caption("037 — Flashlight (exercise)")


def load_shader(path):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path), encoding='utf-8') as f:
        return f.read()


def load_texture(ctx, path):
    base = os.path.dirname(os.path.abspath(__file__))
    image = pygame.image.load(os.path.join(base, path)).convert_alpha()
    image = pygame.transform.flip(image, False, True)
    data  = pygame.image.tostring(image, 'RGBA')
    tex   = ctx.texture(image.get_size(), 4, data)
    tex.build_mipmaps()
    return tex


def load_obj_mesh(path):
    base = os.path.dirname(os.path.abspath(__file__))
    scene = pywavefront.Wavefront(
        os.path.join(base, path), create_materials=True, parse=True,
    )
    all_verts = []
    for mat in scene.materials.values():
        if mat.vertices:
            all_verts.extend(mat.vertices)
    verts = np.array(all_verts, dtype='f4').reshape(-1, 8)
    return np.ascontiguousarray(np.hstack([verts[:, 5:], verts[:, 2:5], verts[:, 0:2]]))


CUBE_POSITIONS = [
    glm.vec3( 0.0,  0.0,  0.0),
    glm.vec3( 2.0,  0.5, -2.0),
    glm.vec3(-1.5, -1.0, -2.5),
    glm.vec3( 3.0, -0.5, -3.0),
    glm.vec3(-3.0,  0.5, -3.5),
    glm.vec3( 0.5,  1.5, -4.5),
    glm.vec3(-2.5,  0.0, -5.0),
    glm.vec3( 2.5,  0.0, -5.0),
    glm.vec3( 0.0, -1.5, -6.5),
    glm.vec3(-1.0,  1.0, -7.0),
]
CUBE_AXES = [
    glm.vec3(1.0, 0.3, 0.5), glm.vec3(0.5, 1.0, 0.3), glm.vec3(0.3, 0.5, 1.0),
    glm.vec3(1.0, 0.0, 0.5), glm.vec3(0.5, 0.0, 1.0), glm.vec3(0.0, 1.0, 0.5),
    glm.vec3(0.5, 1.0, 0.0), glm.vec3(0.0, 0.5, 1.0), glm.vec3(1.0, 0.5, 0.0),
    glm.vec3(0.5, 0.5, 0.5),
]


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.object_program = self.ctx.program(
            vertex_shader=load_shader('shaders/object.vert'),
            fragment_shader=load_shader('shaders/object.frag'),
        )

        vbo = self.ctx.buffer(load_obj_mesh('../models/cube.obj'))
        self.object_vao = self.ctx.vertex_array(
            self.object_program,
            [(vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_uv')],
        )

        load_texture(self.ctx, '../images/container2.png').use(location=0)
        load_texture(self.ctx, '../images/container2_specular.png').use(location=1)

        projection = glm.perspective(glm.radians(45.0), 800.0 / 600.0, 0.1, 100.0)
        self.object_program['projection'].write(projection)

        self.object_program['material.diffuse']   = 0
        self.object_program['material.specular']  = 1
        self.object_program['material.shininess'] = 64.0

        self.cone_angle = 12.5  # inner half-angle in degrees; outer is always +2.5°
        self.object_program['light.cut_off']       = math.cos(math.radians(self.cone_angle))
        self.object_program['light.outer_cut_off'] = math.cos(math.radians(self.cone_angle + 2.5))
        self.object_program['light.ambient']       = (0.0, 0.0, 0.0)
        self.object_program['light.diffuse']       = (1.0, 1.0, 1.0)
        self.object_program['light.specular']      = (1.0, 1.0, 1.0)

        self.cube_transforms = []
        for i, pos in enumerate(CUBE_POSITIONS):
            model = glm.rotate(
                glm.translate(glm.mat4(1.0), pos),
                glm.radians(20.0 * i),
                CUBE_AXES[i],
            )
            nmat = glm.mat3(glm.transpose(glm.inverse(model)))
            self.cube_transforms.append((model, nmat))

        # Camera state
        self.camera_pos   = glm.vec3(0.0, 0.0, 5.0)
        self.camera_front = glm.vec3(0.0, 0.0, -1.0)
        self.camera_up    = glm.vec3(0.0, 1.0,  0.0)
        self.yaw          = -90.0
        self.pitch        =   0.0
        self.speed        =   4.0
        self.sensitivity  =   0.1

        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

    def handle_mouse(self, dx, dy):
        self.yaw   += dx * self.sensitivity
        self.pitch -= dy * self.sensitivity
        self.pitch  = max(-89.0, min(89.0, self.pitch))
        front = glm.vec3(
            math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch)),
            math.sin(glm.radians(self.pitch)),
            math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch)),
        )
        self.camera_front = glm.normalize(front)

    def adjust_cone(self, delta):
        # TODO 2 — update self.cone_angle by delta, clamp to a sensible range,
        # then upload light.cut_off and light.outer_cut_off as cosines
        pass

    def render(self, dt):
        self.ctx.clear(0.0, 0.0, 0.0)

        keys = pygame.key.get_pressed()
        right = glm.normalize(glm.cross(self.camera_front, self.camera_up))
        v = self.speed * dt
        if keys[pygame.K_w]: self.camera_pos += self.camera_front * v
        if keys[pygame.K_s]: self.camera_pos -= self.camera_front * v
        if keys[pygame.K_a]: self.camera_pos -= right * v
        if keys[pygame.K_d]: self.camera_pos += right * v

        view = glm.lookAt(self.camera_pos, self.camera_pos + self.camera_front, self.camera_up)
        self.object_program['view'].write(view)
        self.object_program['u_view_pos'] = tuple(self.camera_pos)

        # TODO 1 — upload the spot light position and direction so the beam follows the camera

        for model, nmat in self.cube_transforms:
            self.object_program['model'].write(model)
            self.object_program['normal_matrix'].write(nmat)
            self.object_vao.render()


scene = Scene()
clock = pygame.time.Clock()

while True:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_UP:
                scene.adjust_cone(+2.5)
            elif event.key == pygame.K_DOWN:
                scene.adjust_cone(-2.5)
        if event.type == pygame.MOUSEMOTION:
            scene.handle_mouse(*event.rel)

    scene.render(dt)
    pygame.display.flip()

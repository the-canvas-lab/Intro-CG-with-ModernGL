# =============================================================================
# Lesson 036 — Light Casters
# =============================================================================
# Three light types share the same scene so you can compare their behaviour
# directly by pressing ← / →.
#
#   0 — Directional   constant direction, no position, no attenuation
#   1 — Point         position + distance attenuation
#   2 — Spot          position + cone cutoff (soft edges)
#
# The directional angle matches the vector from the point / spot position
# toward the scene origin so the shading direction is identical across all
# three modes.  Differences you should notice:
#
#   Directional → Point   same shading angle, but far cubes become darker
#   Point → Spot          same position, but cubes outside the cone go dark
#
# Controls:  ← / → — switch mode   Esc — quit
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


def load_shader(path):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path)) as f:
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


MODES = ["Directional", "Point", "Spot"]

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

# Point and spot share this position.
# The directional angle is the vector from this point toward the origin,
# so all three modes shade from the same apparent direction.
LIGHT_POS = glm.vec3(2.0, 2.0, -6.0)
LIGHT_DIR = glm.normalize(glm.vec3(-2.0, -2.0, 6.0))


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.object_program = self.ctx.program(
            vertex_shader=load_shader('shaders/object.vert'),
            fragment_shader=load_shader('shaders/object.frag'),
        )
        self.lamp_program = self.ctx.program(
            vertex_shader=load_shader('shaders/lamp.vert'),
            fragment_shader=load_shader('shaders/lamp.frag'),
        )

        vbo = self.ctx.buffer(load_obj_mesh('../models/cube.obj'))
        self.object_vao = self.ctx.vertex_array(
            self.object_program,
            [(vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_uv')],
        )
        self.lamp_vao = self.ctx.vertex_array(
            self.lamp_program, [(vbo, '3f 20x', 'in_position')]
        )

        load_texture(self.ctx, '../images/container2.png').use(location=0)
        load_texture(self.ctx, '../images/container2_specular.png').use(location=1)

        camera_pos = glm.vec3(0.0, 0.0, -12.0)
        view       = glm.lookAt(camera_pos, glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))
        projection = glm.perspective(glm.radians(60.0), 800.0 / 600.0, 0.1, 100.0)

        for prog in (self.object_program, self.lamp_program):
            prog['view'].write(view)
            prog['projection'].write(projection)

        self.object_program['u_view_pos'] = tuple(camera_pos)

        self.object_program['material.diffuse']   = 0
        self.object_program['material.specular']  = 1
        self.object_program['material.shininess'] = 64.0

        # All three modes use the same ambient/diffuse/specular intensities.
        self.object_program['light.ambient']  = (0.1, 0.1, 0.1)
        self.object_program['light.diffuse']  = (0.8, 0.8, 0.8)
        self.object_program['light.specular'] = (1.0, 1.0, 1.0)

        # Directional
        self.object_program['light.direction'] = tuple(LIGHT_DIR)

        # Point
        self.object_program['light.position']  = tuple(LIGHT_POS)
        self.object_program['light.constant']  = 1.0
        self.object_program['light.linear']    = 0.09
        self.object_program['light.quadratic'] = 0.032

        # Spot (same position and direction as point)
        self.object_program['light.cut_off']       = math.cos(math.radians(20.0))
        self.object_program['light.outer_cut_off'] = math.cos(math.radians(25.0))

        # Lamp cube at the shared light position (used for point and spot modes)
        lamp_model = glm.scale(glm.translate(glm.mat4(1.0), LIGHT_POS), glm.vec3(0.2))
        self.lamp_program['model'].write(lamp_model)

        self.cube_transforms = []
        for i, pos in enumerate(CUBE_POSITIONS):
            model = glm.rotate(
                glm.translate(glm.mat4(1.0), pos),
                glm.radians(20.0 * i),
                CUBE_AXES[i],
            )
            nmat = glm.mat3(glm.transpose(glm.inverse(model)))
            self.cube_transforms.append((model, nmat))

        self.mode = 0
        self._apply_mode()

    def _apply_mode(self):
        self.object_program['u_mode'] = self.mode
        label = MODES[self.mode]
        pygame.display.set_caption(
            f"036 — Light Casters  [{self.mode + 1}/{len(MODES)}] {label}  (← →)"
        )
        print(f"[{self.mode + 1}/{len(MODES)}] {label}")

    def select_mode(self, delta):
        self.mode = (self.mode + delta) % len(MODES)
        self._apply_mode()

    def render(self, time):
        self.ctx.clear(0.1, 0.1, 0.1)

        for model, nmat in self.cube_transforms:
            self.object_program['model'].write(model)
            self.object_program['normal_matrix'].write(nmat)
            self.object_vao.render()

        # Show the lamp cube only for modes that have a physical light position.
        if self.mode in (1, 2):
            self.lamp_vao.render()


scene = Scene()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_RIGHT:
                scene.select_mode(+1)
            elif event.key == pygame.K_LEFT:
                scene.select_mode(-1)

    scene.render(pygame.time.get_ticks() / 1000.0)
    pygame.display.flip()

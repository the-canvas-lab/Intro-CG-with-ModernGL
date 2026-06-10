# =============================================================================
# Lesson 038 — Depth Testing
# =============================================================================
# The depth buffer stores a non-linear value for every fragment — most of the
# available precision is concentrated near the camera's near plane, leaving
# very little to distinguish objects that are far away.
#
# Switch modes to see this directly:
#
#   0 — Normal          standard textured shading
#   1 — Depth (raw)     gl_FragCoord.z as grayscale — objects at distances
#                       5–12 units all cluster near 1.0 and appear nearly white
#   2 — Depth (linear)  depth linearized back to view-space distance and
#                       normalized by far — shows the actual distance gradient
#
# Controls:  ← / → — switch mode   Esc — quit
# =============================================================================

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


MODES = ["Normal", "Depth (raw)", "Depth (linear)"]

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

NEAR =   0.1
FAR  = 100.0


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.program = self.ctx.program(
            vertex_shader=load_shader('shaders/object.vert'),
            fragment_shader=load_shader('shaders/object.frag'),
        )

        vbo = self.ctx.buffer(load_obj_mesh('../models/cube.obj'))
        self.vao = self.ctx.vertex_array(
            self.program,
            [(vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_uv')],
        )

        load_texture(self.ctx, '../images/container2.png').use(location=0)
        self.program['u_texture'] = 0
        self.program['u_near']    = NEAR
        self.program['u_far']     = FAR

        camera_pos = glm.vec3(0.0, 0.0, 5.0)
        view       = glm.lookAt(camera_pos, glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))
        projection = glm.perspective(glm.radians(45.0), 800.0 / 600.0, NEAR, FAR)

        self.program['view'].write(view)
        self.program['projection'].write(projection)

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
        self.program['u_mode'] = self.mode
        label = MODES[self.mode]
        pygame.display.set_caption(
            f"038 — Depth Testing  [{self.mode + 1}/{len(MODES)}] {label}  (← →)"
        )
        print(f"[{self.mode + 1}/{len(MODES)}] {label}")

    def select_mode(self, delta):
        self.mode = (self.mode + delta) % len(MODES)
        self._apply_mode()

    def render(self):
        self.ctx.clear(0.1, 0.1, 0.1)

        for model, nmat in self.cube_transforms:
            self.program['model'].write(model)
            self.program['normal_matrix'].write(nmat)
            self.vao.render()


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

    scene.render()
    pygame.display.flip()

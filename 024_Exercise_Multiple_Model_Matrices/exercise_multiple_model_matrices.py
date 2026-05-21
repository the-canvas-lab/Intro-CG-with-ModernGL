# =============================================================================
# Exercise 024 — Multiple Cubes
# =============================================================================
# Goal: render 10 cubes scattered in 3D space, each with a unique rotation,
#       and make every third cube spin over time.
#
# Background
# ----------
# The view and projection matrices are shared across all objects in a scene —
# they describe the camera and lens, not the objects themselves. The model
# matrix is the only one that changes per object: each cube has its own
# position and orientation in world space.
#
# Tasks
# -----
# 1. Inside the loop over CUBE_POSITIONS, build a model matrix that:
#      - Translates the cube to its position
#      - Rotates it by  20 * i  degrees around  glm.vec3(1.0, 0.3, 0.5)
#    The result: 10 cubes spread through space, each tilted at a different angle.
#
# 2. For cubes where  i % 3 == 0  (indices 0, 3, 6, 9), add an additional
#    rotation by  time  radians around the same axis so those cubes spin.
#
# Expected result: a field of textured cubes at various depths; four of them
#                  rotate continuously while the others hold their tilt.
# =============================================================================

import os
import sys

import glm
import moderngl
import numpy as np
import pygame

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

# fmt: off
CUBE_VERTICES = np.array([
    -0.5, -0.5, -0.5,  0.0, 0.0,
     0.5, -0.5, -0.5,  1.0, 0.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
    -0.5,  0.5, -0.5,  0.0, 1.0,
    -0.5, -0.5, -0.5,  0.0, 0.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,
     0.5, -0.5,  0.5,  1.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 1.0,
     0.5,  0.5,  0.5,  1.0, 1.0,
    -0.5,  0.5,  0.5,  0.0, 1.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,
    -0.5,  0.5,  0.5,  1.0, 0.0,
    -0.5,  0.5, -0.5,  1.0, 1.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,
    -0.5,  0.5,  0.5,  1.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 0.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
     0.5, -0.5, -0.5,  0.0, 1.0,
     0.5, -0.5, -0.5,  0.0, 1.0,
     0.5, -0.5,  0.5,  0.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 0.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,
     0.5, -0.5, -0.5,  1.0, 1.0,
     0.5, -0.5,  0.5,  1.0, 0.0,
     0.5, -0.5,  0.5,  1.0, 0.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,
    -0.5,  0.5, -0.5,  0.0, 1.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
     0.5,  0.5,  0.5,  1.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 0.0,
    -0.5,  0.5,  0.5,  0.0, 0.0,
    -0.5,  0.5, -0.5,  0.0, 1.0,
], dtype='f4')

CUBE_POSITIONS = [
    glm.vec3( 0.0,  0.0,  0.0),
    glm.vec3( 2.0,  5.0, -15.0),
    glm.vec3(-1.5, -2.2,  -2.5),
    glm.vec3(-3.8, -2.0, -12.3),
    glm.vec3( 2.4, -0.4,  -3.5),
    glm.vec3(-1.7,  3.0,  -7.5),
    glm.vec3( 1.3, -2.0,  -2.5),
    glm.vec3( 1.5,  2.0,  -2.5),
    glm.vec3( 1.5,  0.2,  -1.5),
    glm.vec3(-1.3,  1.0,  -1.5),
]
# fmt: on

ROTATION_AXIS = glm.vec3(1.0, 0.3, 0.5)


def load_shader(path):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path), encoding='utf-8') as f:
        return f.read()


def load_texture(ctx, path):
    base = os.path.dirname(os.path.abspath(__file__))
    image = pygame.image.load(os.path.join(base, path)).convert_alpha()
    image = pygame.transform.flip(image, False, True)
    data = pygame.image.tostring(image, 'RGBA')
    texture = ctx.texture(image.get_size(), 4, data)
    texture.build_mipmaps()
    return texture


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(self.ctx.DEPTH_TEST)

        self.program = self.ctx.program(
            vertex_shader=load_shader('shaders/cube.vert'),
            fragment_shader=load_shader('shaders/cube.frag'),
        )

        vbo = self.ctx.buffer(CUBE_VERTICES)
        self.vao = self.ctx.vertex_array(
            self.program,
            [(vbo, '3f 2f', 'in_position', 'in_uv')],
        )

        self.texture = load_texture(self.ctx, '../images/container.jpg')
        self.program['u_texture'] = 0

        projection = glm.perspective(glm.radians(45.0), 800 / 600, 0.1, 100.0)
        self.program['u_projection'].write(projection)

        view = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, -3.0))
        self.program['u_view'].write(view)

    def render(self, time):
        self.ctx.clear()
        self.texture.use(location=0)

        for i, pos in enumerate(CUBE_POSITIONS):
            # TODO (Task 1): Build a model matrix that translates to `pos` and
            # rotates by  glm.radians(20.0 * i)  around  ROTATION_AXIS.
            #
            # TODO (Task 2): If  i % 3 == 0,  add a second rotation by  time
            # radians around  ROTATION_AXIS  so those cubes spin continuously.

            model = glm.mat4(1.0)          # placeholder — replace with your transform
            self.program['u_model'].write(model)
            self.vao.render()


scene = Scene()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    time = pygame.time.get_ticks() / 1000.0
    scene.render(time)
    pygame.display.flip()

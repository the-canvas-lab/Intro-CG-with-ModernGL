# =============================================================================
# Exercise 022 — Transform Order
# =============================================================================
# Goal: observe how the order of matrix operations changes the result, then
#       draw a second quad that scales over time using sin().
#
# Background
# ----------
# In lesson 021 the transform is built as  T * R * S  (translate, rotate, scale).
# Because the GPU applies the operations right-to-left (S → R → T), the quad
# is first scaled, then rotated around the world origin, then moved to (0.5, -0.5).
# The result is a quad that spins in place at the bottom-right corner.
#
# Tasks
# -----
# 1. In the first quad's transform, swap the translate and rotate lines so the
#    matrix becomes  R * T * S  instead of  T * R * S.
#    Run the program — the motion should change from spinning-in-place to orbiting
#    around the world origin.  Think about why: with  R * T * S  the vertices are
#    scaled, then moved to (0.5, -0.5), then rotated around (0, 0).
#
# 2. Uncomment the second quad's render block and fill in its transform so that:
#    - It is positioned in the top-left area  (-0.5, 0.5)
#    - Its size pulses using  sin(time)  applied as the scale factor
#    - No rotation
#    Note: sin() passes through zero and goes negative — when the scale is negative
#    the image flips.  This is expected behaviour, not a bug.
# =============================================================================

import math
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

        self.program = self.ctx.program(
            vertex_shader=load_shader('shaders/rect.vert'),
            fragment_shader=load_shader('shaders/rect.frag'),
        )

        vertices = np.array([
            # x      y     z     u    v
             0.5,  0.5,  0.0,  1.0, 1.0,
             0.5, -0.5,  0.0,  1.0, 0.0,
            -0.5, -0.5,  0.0,  0.0, 0.0,
            -0.5,  0.5,  0.0,  0.0, 1.0,
        ], dtype='f4')
        indices = np.array([0, 1, 3, 1, 2, 3], dtype='i4')

        vbo = self.ctx.buffer(vertices)
        ibo = self.ctx.buffer(indices)
        self.vao = self.ctx.vertex_array(
            self.program,
            [(vbo, '3f 2f', 'in_position', 'in_uv')],
            ibo,
        )

        self.texture = load_texture(self.ctx, '../images/numbers.png')
        self.program['u_texture'] = 0

    def render(self, time):
        self.ctx.clear()
        self.texture.use(location=0)

        # ── Quad 1 ──────────────────────────────────────────────────────────
        # TODO (Task 1): Swap the translate and rotate lines so the matrix
        # becomes R * T * S instead of T * R * S, then observe the difference.
        transform1 = glm.mat4(1.0)
        transform1 = glm.translate(transform1, glm.vec3(0.5, -0.5, 0.0))    # ③
        transform1 = glm.rotate(transform1, time, glm.vec3(0.0, 0.0, 1.0))  # ②
        transform1 = glm.scale(transform1, glm.vec3(0.5, 0.5, 0.5))         # ①

        self.program['u_transform'].write(transform1)
        self.vao.render()

        # ── Quad 2 ──────────────────────────────────────────────────────────
        # TODO (Task 2): Build transform2 and uncomment the two lines below.
        #   - Translate to (-0.5, 0.5, 0.0)
        #   - Scale by (sin(time), sin(time), 1.0)  — no rotation

        # transform2 = ...
        # self.program['u_transform'].write(transform2)
        # self.vao.render()


scene = Scene()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    time = pygame.time.get_ticks() / 1000.0
    scene.render(time)
    pygame.display.flip()

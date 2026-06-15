# =============================================================================
# Exercise 013 — Pulsing Rectangle
# =============================================================================
# Goal: render a rectangle where the two vertices on the shared diagonal are
#       red and pulse in brightness over time, while the other two vertices
#       stay black.
#
#   Vertex layout (indices 0-3):
#
#       3 (top left) -------- 0 (top right)
#            |              / |
#            |            /   |
#            |          /     |
#       2 (bottom left) ---- 1 (bottom right)
#
#   Shared diagonal: vertices 1 and 3  → red,  pulsing
#   Other corners  : vertices 0 and 2  → black, always dark
#
# Tasks
# -----
# 1. Fill in 4 interleaved vertices (x, y, z, r, g, b).
#    Assign red (1,0,0) to the diagonal vertices and black (0,0,0) to the rest.
#
# 2. Fill in the index buffer — two triangles covering the rectangle.
#    Refer to program 006 if needed.
#
# 3. Create the rectangle VAO with the index buffer bound.
#
# 4. Update the u_time uniform each frame.
#
# 5. Complete the vertex shader (shaders/rectangle.vert): declare attributes,
#    compute brightness from u_time, and apply it to in_color.
#
# 6. Complete the fragment shader (shaders/rectangle.frag): pass v_color through.
#
# Expected result: a rectangle whose red diagonal pulses between black and red
#                  while the other two corners remain black at all times.
# =============================================================================

import os
import sys

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
pygame.display.gl_set_attribute(
    pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG,
    True
)
pygame.display.set_mode((800, 600), flags=pygame.OPENGL | pygame.DOUBLEBUF, vsync=True)


def load_shader(path):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path), encoding='utf-8') as f:
        return f.read()


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()

        self.program = self.ctx.program(
            vertex_shader=load_shader('shaders/rectangle.vert'),
            fragment_shader=load_shader('shaders/rectangle.frag'),
        )

        # TODO (Task 1): Define 4 interleaved vertices: x, y, z, r, g, b.
        # Diagonal vertices (1 and 3) → red (1, 0, 0)
        # Other vertices   (0 and 2) → black (0, 0, 0)
        vertices = np.array([
            # x      y      z     r     g     b
            # 0: top right
            # 1: bottom right
            # 2: bottom left
            # 3: top left
        ], dtype='f4')

        # TODO (Task 2): Define 6 indices — two triangles covering the rectangle.
        indices = np.array([
            # ...
        ], dtype='i4')

        self.vbo = self.ctx.buffer(vertices)
        self.ibo = self.ctx.buffer(indices)

        # TODO (Task 3): Create the VAO with the index buffer.
        # Hint: use '3f 3f' for the interleaved position + color attributes.
        self.vao = None

    def render(self, time):
        self.ctx.clear()
        self.ctx.enable(self.ctx.DEPTH_TEST)

        # TODO (Task 4): Set the u_time uniform.

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

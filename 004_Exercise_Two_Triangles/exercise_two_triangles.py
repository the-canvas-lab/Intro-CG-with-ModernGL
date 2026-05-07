# =============================================================================
# Exercise 004 — Two Triangles with Per-Vertex Color
# =============================================================================
# Goal: render two triangles side by side, each with a different solid color,
#       using a single draw call.
#
# Tasks
# -----
# 1. Fill in the vertex data below (positions + colors for 6 vertices).
#    - Left triangle  : center it on the left half of the screen.
#    - Right triangle : center it on the right half of the screen.
#    - Assign a distinct RGB color to every vertex of each triangle.
#      (Tip: giving all three vertices of one triangle the same color keeps
#       the result visually clear.)
#
# 2. Complete the VAO binding so the GPU knows how to split each row of the
#    buffer into a position attribute and a color attribute.
#
# 3. Fill in the missing GLSL code in shaders/triangle.vert and
#    shaders/triangle.frag (look for TODO comments there).
#
# Expected result: two solid-colored triangles, one on each side of the window.
# =============================================================================

import os
import sys

import moderngl
import numpy as np
import pygame

os.environ['SDL_WINDOWS_DPI_AWARENESS'] = 'permonitorv2'

pygame.init()
pygame.display.set_mode((800, 600), flags=pygame.OPENGL | pygame.DOUBLEBUF, vsync=True)


def load_shader(path):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path)) as f:
        return f.read()


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()

        self.program = self.ctx.program(
            vertex_shader=load_shader('shaders/triangle.vert'),
            fragment_shader=load_shader('shaders/triangle.frag'),
        )

        # TODO: Define 6 vertices — 3 for the left triangle, 3 for the right.
        # Each row holds: x, y, z, r, g, b  (all float32, range -1..1 for
        # positions and 0..1 for colors).
        # Replace the placeholder below with your actual values.
        vertices = np.array([
            # x      y      z     r     g     b
            # --- left triangle ---
            # ...
            # ...
            # ...
            # --- right triangle ---
            # ...
            # ...
            # ...
        ], dtype='f4')

        self.vbo = self.ctx.buffer(vertices)

        # TODO: Complete the format string so the VAO knows each vertex
        # contains two attributes: a 3-float position and a 3-float color.
        # Also provide both attribute names as they appear in the vertex shader.
        #
        # Hint: the format string for two consecutive 3-float attributes is '3f 3f'.
        self.vao = self.ctx.vertex_array(self.program, [
            (self.vbo, '3f', 'in_position'),  # <-- extend this line
        ])

    def render(self):
        self.ctx.clear()
        self.ctx.enable(self.ctx.DEPTH_TEST)
        self.vao.render()


scene = Scene()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    scene.render()

    pygame.display.flip()

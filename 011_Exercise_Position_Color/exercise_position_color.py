# =============================================================================
# Exercise 011 — Position as Color
# =============================================================================
# Goal: pass vertex position through to the fragment shader as a color, then
#       observe how fragment interpolation (see 010/README.md) shapes the result.
#
# Tasks
# -----
# 1. In shaders/triangle.vert:
#    - Declare v_color as a vec3 output.
#    - Assign in_position directly to v_color.
#
# 2. In shaders/triangle.frag:
#    - Declare v_color as a vec3 input.
#    - Output it as the fragment color (alpha = 1.0).
#
# 3. After it works, think about these questions:
#    - Parts of the triangle appear black even though no vertex was colored black.
#      Why does this happen?
#    - Which axis controls the red channel? Which controls the green?
#    - What does the blue channel look like, and why is it constant?
#
# Expected result: a triangle with a color gradient where negative position
#                  values produce black due to clamping.
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

        vertices = np.array([
            -0.5, -0.5, 0.0,
             0.5, -0.5, 0.0,
             0.0,  0.5, 0.0,
        ], dtype='f4')

        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.vertex_array(self.program, [(self.vbo, '3f', 'in_position')])

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

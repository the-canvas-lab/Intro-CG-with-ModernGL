# =============================================================================
# Exercise 015 — Flip and Offset
# =============================================================================
# Goal: modify the vertex shader to flip the triangle upside down and translate
#       it using a vec2 uniform updated every frame from the CPU.
#
# Tasks
# -----
# 1. In shaders/triangle.vert, negate the y component of in_position to flip
#    the triangle vertically.
#
# 2. In shaders/triangle.vert, add u_offset to the x and y components so the
#    triangle moves with the animated uniform.
#
# The Python side is already complete — it animates u_offset automatically.
#
# Expected result: an upside-down triangle that oscillates left and right.
#                  If the flip is missing, the triangle points upward.
#                  If the offset is missing, the triangle stays centered.
# =============================================================================

import os
import sys
import math

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

    def render(self, time):
        self.ctx.clear()
        self.ctx.enable(self.ctx.DEPTH_TEST)

        # Oscillate horizontally between -0.5 and 0.5.
        self.program['u_offset'] = (math.sin(time) * 0.5, 0.0)

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

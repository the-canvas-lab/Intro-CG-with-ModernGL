# =============================================================================
# Exercise 009 — Rectangle and Triangle with Separate Shaders
# =============================================================================
# Goal: render an orange rectangle on the left and a blue triangle on the
#       right using fully independent VAO/VBO pairs and separate shader programs.
#
# Tasks
# -----
# 1. (shaders/rectangle.frag) Set the rectangle color to orange.
# 2. (shaders/triangle.frag)  Set the triangle color to blue.
#
# 3. Fill in the 4 unique rectangle vertices on the LEFT half of the screen.
#    Refer to program 006 for the vertex layout.
#
# 4. Fill in the index buffer so that the two indices arrays form two triangles
#    that together cover the rectangle.
#
# 5. Create the rectangle VAO with the index buffer bound.
#    Refer to program 006 for the vertex_array arguments.
#
# 6. Fill in the 3 triangle vertices on the RIGHT half of the screen.
#
# 7. Create the triangle VAO (no index buffer needed).
#
# Expected result: an orange rectangle on the left, a blue triangle on the right.
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

        self.rect_program = self.ctx.program(
            vertex_shader=load_shader('shaders/rectangle.vert'),
            fragment_shader=load_shader('shaders/rectangle.frag'),
        )
        self.tri_program = self.ctx.program(
            vertex_shader=load_shader('shaders/triangle.vert'),
            fragment_shader=load_shader('shaders/triangle.frag'),
        )

        # --- Rectangle (left half) -------------------------------------------

        # TODO (Task 3): Define 4 unique vertices for a rectangle on the left
        # half of the screen. Each vertex is (x, y, z).
        rect_vertices = np.array([
            # x      y      z
            # ...
        ], dtype='f4')

        # TODO (Task 4): Define the index buffer. Two triangles, 3 indices each.
        rect_indices = np.array([
            # ...
        ], dtype='i4')

        self.rect_vbo = self.ctx.buffer(rect_vertices)
        self.rect_ibo = self.ctx.buffer(rect_indices)

        # TODO (Task 5): Create the rectangle VAO with the index buffer.
        # Hint: add index_buffer=self.rect_ibo and index_element_size=4.
        self.rect_vao = self.ctx.vertex_array(
            self.rect_program,
            [(self.rect_vbo, '3f', 'in_position')],
            # ...
        )

        # --- Triangle (right half) -------------------------------------------

        # TODO (Task 6): Define 3 vertices for a triangle on the right half.
        tri_vertices = np.array([
            # x      y      z
            # ...
        ], dtype='f4')

        self.tri_vbo = self.ctx.buffer(tri_vertices)

        # TODO (Task 7): Create the triangle VAO (no index buffer).
        self.tri_vao = None

    def render(self):
        self.ctx.clear()
        self.ctx.enable(self.ctx.DEPTH_TEST)
        self.rect_vao.render()
        self.tri_vao.render()


scene = Scene()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    scene.render()

    pygame.display.flip()

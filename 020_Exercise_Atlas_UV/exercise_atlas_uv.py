# =============================================================================
# Exercise 020 — Atlas UV Mapping
# =============================================================================
# Goal: display all six numbers from a texture atlas by assigning the correct
#       UV coordinates to each of the six on-screen quads.
#
# A texture atlas packs multiple images into one texture file. Each image
# occupies a rectangular region, and UV coordinates select which region a
# quad samples from. This is exactly the UV mapping step performed inside
# tools like Blender when an artist assigns a part of a texture to a mesh face.
#
# The atlas (numbers.png) is a 3-column × 2-row grid:
#
#   image as seen in a viewer (top-left origin):
#   +----------+----------+----------+
#   |    1     |    2     |    3     |  ← image row 0 (top)
#   +----------+----------+----------+
#   |    4     |    5     |    6     |  ← image row 1 (bottom)
#   +----------+----------+----------+
#
# After the vertical flip applied on load (OpenGL origin is bottom-left),
# the UV layout becomes:
#
#   v = 1.0  ┌──────────┬──────────┬──────────┐
#            │    1     │    2     │    3     │
#   v = 0.5  ├──────────┼──────────┼──────────┤
#            │    4     │    5     │    6     │
#   v = 0.0  └──────────┴──────────┴──────────┘
#           u = 0.0   1/3       2/3       1.0
#
# Tasks
# -----
# Fill in u0, u1, v0, v1 for each of the six quads below so that:
#   - The top row of quads shows numbers 1, 2, 3 (left to right)
#   - The bottom row of quads shows numbers 4, 5, 6 (left to right)
#
# Hint: each column spans 1/3 of the texture width.
#       Numbers 1-3 are in the upper half of UV space (v: 0.5 → 1.0).
#       Numbers 4-6 are in the lower half of UV space (v: 0.0 → 0.5).
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

        self.texture = load_texture(self.ctx, '../images/numbers.png')
        self.program['u_texture'] = 0

        # TODO: Replace each 0.0 placeholder with the correct UV value.
        #
        #   _make_quad(x0, x1, y0, y1,  u0,  u1,  v0,  v1)
        #                               ^^^^^^^^^^^^^^^^^^^
        #                               these are what you fill in

        self.quads = [
            # ── top row: should show 1, 2, 3 ──────────────────────────────
            self._make_quad(*self._bounds(0, 0), 0.0, 0.0, 0.0, 0.0),  # show 1
            self._make_quad(*self._bounds(1, 0), 0.0, 0.0, 0.0, 0.0),  # show 2
            self._make_quad(*self._bounds(2, 0), 0.0, 0.0, 0.0, 0.0),  # show 3
            # ── bottom row: should show 4, 5, 6 ───────────────────────────
            self._make_quad(*self._bounds(0, 1), 0.0, 0.0, 0.0, 0.0),  # show 4
            self._make_quad(*self._bounds(1, 1), 0.0, 0.0, 0.0, 0.0),  # show 5
            self._make_quad(*self._bounds(2, 1), 0.0, 0.0, 0.0, 0.0),  # show 6
        ]

    def _bounds(self, col, row):
        """NDC screen bounds for grid cell (col, row)."""
        cell_w = 0.56
        cell_h = 0.80
        gap_x = (2.0 - 3 * cell_w) / 4
        gap_y = (2.0 - 2 * cell_h) / 3
        x0 = -1.0 + gap_x + col * (cell_w + gap_x)
        x1 = x0 + cell_w
        y1 = 1.0 - gap_y - row * (cell_h + gap_y)
        y0 = y1 - cell_h
        return x0, x1, y0, y1

    def _make_quad(self, x0, x1, y0, y1, u0, u1, v0, v1):
        vertices = np.array([
            # x    y     z    u   v
            x1,  y1,  0.0,  u1, v1,   # top right
            x1,  y0,  0.0,  u1, v0,   # bottom right
            x0,  y0,  0.0,  u0, v0,   # bottom left
            x0,  y1,  0.0,  u0, v1,   # top left
        ], dtype='f4')
        indices = np.array([0, 1, 3, 1, 2, 3], dtype='i4')
        vbo = self.ctx.buffer(vertices)
        ibo = self.ctx.buffer(indices)
        return self.ctx.vertex_array(
            self.program,
            [(vbo, '3f 2f', 'in_position', 'in_uv')],
            ibo,
        )

    def render(self):
        self.ctx.clear()
        self.texture.use(location=0)
        for quad in self.quads:
            quad.render()


scene = Scene()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    scene.render()
    pygame.display.flip()

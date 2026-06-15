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
            vertex_shader=load_shader('shaders/triangle.vert'),
            fragment_shader=load_shader('shaders/triangle.frag'),
        )

        # In program 003, the buffer held only positions (3 floats per vertex).
        # Here we pack BOTH position and color for each vertex into the same
        # buffer, one after the other. This layout is called interleaved data:
        #
        #   |<-------- vertex 0 -------->|<-------- vertex 1 -------->| ...
        #   [ x   y   z   r   g   b  ]  [ x   y   z   r   g   b  ]  ...
        #     0   4   8  12  16  20       24  28  32  36  40  44     (byte offset)
        #
        # Stride: the number of bytes from the start of one vertex to the next.
        #         6 floats × 4 bytes = 24 bytes.
        #
        # Offset: the number of bytes from the start of a vertex to a specific
        #         attribute.
        #         - in_position starts at byte 0  (first attribute)
        #         - in_color    starts at byte 12 (after 3 floats × 4 bytes)
        #
        # In moderngl the format string encodes stride and offset automatically:
        #   '3f 3f' → two attributes, each 3 floats, packed consecutively.
        # The stride is inferred as the total size (24 bytes), and the offset
        # of each attribute is derived from the sizes of the ones before it.
        vertices = np.array([
            # x      y      z      r     g     b
            -0.5,  -0.5,   0.0,   1.0,  0.0,  0.0,   # bottom left  — red
             0.5,  -0.5,   0.0,   0.0,  1.0,  0.0,   # bottom right — green
             0.0,   0.5,   0.0,   0.0,  0.0,  1.0,   # top          — blue
        ], dtype='f4')

        self.vbo = self.ctx.buffer(vertices)

        # '3f 3f' tells the VAO:
        #   - read 3 floats → feed into 'in_position'
        #   - read 3 floats → feed into 'in_color'
        # The GPU steps through the buffer 24 bytes at a time (the stride),
        # starting each attribute at its computed offset within that stride.
        self.vao = self.ctx.vertex_array(
            self.program,
            [(self.vbo, '3f 3f', 'in_position', 'in_color')],
        )

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

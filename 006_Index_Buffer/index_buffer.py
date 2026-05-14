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
    with open(os.path.join(base, path)) as f:
        return f.read()


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()

        self.program = self.ctx.program(
            vertex_shader=load_shader('shaders/rectangle.vert'),
            fragment_shader=load_shader('shaders/rectangle.frag'),
        )

        # Only 4 unique corners are needed — no duplicates.
        # In 005 we repeated bottom-right and top-left to form two triangles;
        # here the index buffer handles that reuse instead.
        vertices = np.array([
             0.5,  0.5, 0.0,   # 0: top right
             0.5, -0.5, 0.0,   # 1: bottom right
            -0.5, -0.5, 0.0,   # 2: bottom left
            -0.5,  0.5, 0.0,   # 3: top left
        ], dtype='f4')

        # The index buffer (IBO / EBO) tells the GPU which vertices to combine
        # into triangles, referencing them by their position in the vertex buffer.
        # Each triple is one triangle:
        #   triangle 1 → vertices 0, 1, 3  (top right, bottom right, top left)
        #   triangle 2 → vertices 1, 2, 3  (bottom right, bottom left, top left)
        # The two shared vertices (1 and 3) are stored once but referenced twice,
        # saving memory and bandwidth as geometry grows more complex.
        indices = np.array([
            0, 1, 3,
            1, 2, 3,
        ], dtype='i4')

        self.vbo = self.ctx.buffer(vertices)
        self.ibo = self.ctx.buffer(indices)

        # Pass the index buffer to vertex_array via the 'index_buffer' argument.
        # moderngl will issue an indexed draw call (glDrawElements) automatically.
        self.vao = self.ctx.vertex_array(
            self.program,
            [(self.vbo, '3f', 'in_position')],
            index_buffer=self.ibo,
            index_element_size=4,   # 4 bytes per index → matches dtype='i4'
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

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

        # A rectangle has no primitive that maps to it directly in OpenGL —
        # everything is decomposed into triangles. Here we use 6 vertices to
        # describe two triangles that together cover the rectangle.
        # The bottom-right corner (-0.5, -0.5) and top-left corner (0.5, 0.5)
        # are each listed twice because both triangles share those edges.
        vertices = np.array([
            # first triangle
             0.5,  0.5, 0.0,   # top right
             0.5, -0.5, 0.0,   # bottom right
            -0.5,  0.5, 0.0,   # top left
            # second triangle
             0.5, -0.5, 0.0,   # bottom right  (duplicate)
            -0.5, -0.5, 0.0,   # bottom left
            -0.5,  0.5, 0.0,   # top left      (duplicate)
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

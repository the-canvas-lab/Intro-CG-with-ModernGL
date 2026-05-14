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
            vertex_shader=load_shader('shaders/triangle.vert'),
            fragment_shader=load_shader('shaders/triangle.frag'),
        )

        # Each triangle gets its own VBO and VAO, completely independent of
        # the other. This is the key idea: rather than packing all geometry
        # into one buffer, each object owns its GPU resources separately.

        vertices1 = np.array([
            -0.9, -0.5, 0.0,
            -0.1, -0.5, 0.0,
            -0.5,  0.5, 0.0,
        ], dtype='f4')

        self.vbo1 = self.ctx.buffer(vertices1)
        self.vao1 = self.ctx.vertex_array(self.program, [(self.vbo1, '3f', 'in_position')])

        vertices2 = np.array([
             0.1, -0.5, 0.0,
             0.9, -0.5, 0.0,
             0.5,  0.5, 0.0,
        ], dtype='f4')

        self.vbo2 = self.ctx.buffer(vertices2)
        self.vao2 = self.ctx.vertex_array(self.program, [(self.vbo2, '3f', 'in_position')])

    def render(self):
        self.ctx.clear()
        self.ctx.enable(self.ctx.DEPTH_TEST)

        # Rendering each object is just a .render() call on its own VAO —
        # no manual bind/unbind needed, unlike raw OpenGL.
        self.vao1.render()
        self.vao2.render()


scene = Scene()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    scene.render()

    pygame.display.flip()

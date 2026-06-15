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

        vert = load_shader('shaders/triangle.vert')

        # Each program pairs the same vertex shader with a different fragment
        # shader. The vertex shader is shared in source but compiled separately
        # into each program — the GPU treats them as fully independent pipelines.
        self.program1 = self.ctx.program(
            vertex_shader=vert,
            fragment_shader=load_shader('shaders/triangle_orange.frag'),
        )
        self.program2 = self.ctx.program(
            vertex_shader=vert,
            fragment_shader=load_shader('shaders/triangle_blue.frag'),
        )

        vertices1 = np.array([
            -0.9, -0.5, 0.0,
            -0.1, -0.5, 0.0,
            -0.5,  0.5, 0.0,
        ], dtype='f4')

        vertices2 = np.array([
             0.1, -0.5, 0.0,
             0.9, -0.5, 0.0,
             0.5,  0.5, 0.0,
        ], dtype='f4')

        self.vbo1 = self.ctx.buffer(vertices1)
        self.vbo2 = self.ctx.buffer(vertices2)

        # Each VAO is bound to its own program, so rendering vao1 uses
        # program1 (orange) and rendering vao2 uses program2 (blue).
        self.vao1 = self.ctx.vertex_array(self.program1, [(self.vbo1, '3f', 'in_position')])
        self.vao2 = self.ctx.vertex_array(self.program2, [(self.vbo2, '3f', 'in_position')])

    def render(self):
        self.ctx.clear()
        self.ctx.enable(self.ctx.DEPTH_TEST)
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

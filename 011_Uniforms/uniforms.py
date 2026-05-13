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

        # Write a new value into the uniform every frame.
        # moderngl looks up 'u_time' by name in the compiled shader program
        # and sends the value to the GPU before the draw call.
        # The shader receives the same value for every fragment it processes.
        self.program['u_time'] = time

        self.vao.render()


scene = Scene()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # pygame.time.get_ticks() returns milliseconds since startup.
    # Dividing by 1000 gives seconds, which feeds naturally into sin().
    time = pygame.time.get_ticks() / 1000.0
    scene.render(time)

    pygame.display.flip()

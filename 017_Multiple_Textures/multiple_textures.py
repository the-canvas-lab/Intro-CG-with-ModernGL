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
    with open(os.path.join(base, path), encoding='utf-8') as f:
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

        vertices = np.array([
            # x      y     z     u    v
             0.5,  0.5,  0.0,  1.0, 1.0,
             0.5, -0.5,  0.0,  1.0, 0.0,
            -0.5, -0.5,  0.0,  0.0, 0.0,
            -0.5,  0.5,  0.0,  0.0, 1.0,
        ], dtype='f4')

        indices = np.array([0, 1, 3, 1, 2, 3], dtype='i4')

        self.vbo = self.ctx.buffer(vertices)
        self.ibo = self.ctx.buffer(indices)
        self.vao = self.ctx.vertex_array(
            self.program,
            [(self.vbo, '3f 2f', 'in_position', 'in_uv')],
            self.ibo,
        )

        self.texture0 = load_texture(self.ctx, '../images/container.jpg')
        self.texture1 = load_texture(self.ctx, '../images/awesomeface.png')

        # Each sampler uniform is set to a texture unit number.
        # At draw time, we bind each texture to its corresponding unit.
        # The GPU can access up to 16 texture units (GL_TEXTURE0–GL_TEXTURE15)
        # simultaneously within a single draw call.
        self.program['u_texture0'] = 0
        self.program['u_texture1'] = 1

    def render(self):
        self.ctx.clear()
        self.texture0.use(location=0)
        self.texture1.use(location=1)
        self.vao.render()


scene = Scene()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    scene.render()
    pygame.display.flip()

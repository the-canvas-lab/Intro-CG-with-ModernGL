import os
import sys

import glm
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

        vbo = self.ctx.buffer(vertices)
        ibo = self.ctx.buffer(indices)
        self.vao = self.ctx.vertex_array(
            self.program,
            [(vbo, '3f 2f', 'in_position', 'in_uv')],
            ibo,
        )

        self.texture = load_texture(self.ctx, '../images/container.jpg')
        self.program['u_texture'] = 0

    def render(self, time):
        self.ctx.clear()

        # Each glm call returns a new matrix with the operation appended on the right:
        #   glm.translate(m, v)  →  m * T
        #   glm.rotate(m, a, ax) →  m * R
        #   glm.scale(m, v)      →  m * S
        #
        # The final matrix is  T * R * S.
        # When the GPU computes  (T * R * S) * vertex  it processes right-to-left:
        #   ① S scales the vertex down to 50 %
        #   ② R rotates it around the Z axis
        #   ③ T moves it to the bottom-right corner
        #
        # Read the three lines below bottom-to-top to follow the geometry.
        transform = glm.mat4(1.0)
        transform = glm.translate(transform, glm.vec3(0.5, -0.5, 0.0))    # ③ translate
        transform = glm.rotate(transform, time, glm.vec3(0.0, 0.0, 1.0))  # ② rotate
        transform = glm.scale(transform, glm.vec3(0.5, 0.5, 0.5))         # ① scale

        # pyglm mat4 implements the buffer protocol — moderngl writes it directly.
        self.program['u_transform'].write(transform)

        self.texture.use(location=0)
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

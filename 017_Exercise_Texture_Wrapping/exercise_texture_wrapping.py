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


def load_texture(ctx, path, repeat):
    base = os.path.dirname(os.path.abspath(__file__))
    image = pygame.image.load(os.path.join(base, path)).convert_alpha()
    image = pygame.transform.flip(image, False, True)
    data = pygame.image.tostring(image, 'RGBA')
    texture = ctx.texture(image.get_size(), 4, data)
    texture.build_mipmaps()
    # repeat_x / repeat_y control what happens when a UV coordinate falls
    # outside the 0–1 range:
    #   True  → GL_REPEAT:        tile the texture
    #   False → GL_CLAMP_TO_EDGE: stretch the outermost edge pixel
    texture.repeat_x = repeat
    texture.repeat_y = repeat
    return texture


# TODO: Change WRAP_REPEAT to False and observe how the result changes.
#   True  — the texture tiles to fill the quad (you see a 2×2 grid)
#   False — the edge pixels stretch outward from the centre image
WRAP_REPEAT = True


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()

        self.program = self.ctx.program(
            vertex_shader=load_shader('shaders/rect.vert'),
            fragment_shader=load_shader('shaders/rect.frag'),
        )

        # UVs span 0.0 to 2.0, so the texture is asked to cover twice its
        # natural size on each axis.  The wrapping mode decides what fills
        # the area beyond UV 1.0.
        vertices = np.array([
            # x      y     z     u    v
             0.5,  0.5,  0.0,  2.0, 2.0,   # top right
             0.5, -0.5,  0.0,  2.0, 0.0,   # bottom right
            -0.5, -0.5,  0.0,  0.0, 0.0,   # bottom left
            -0.5,  0.5,  0.0,  0.0, 2.0,   # top left
        ], dtype='f4')

        indices = np.array([0, 1, 3, 1, 2, 3], dtype='i4')

        self.vbo = self.ctx.buffer(vertices)
        self.ibo = self.ctx.buffer(indices)
        self.vao = self.ctx.vertex_array(
            self.program,
            [(self.vbo, '3f 2f', 'in_position', 'in_uv')],
            self.ibo,
        )

        self.texture = load_texture(self.ctx, '../images/container.jpg', WRAP_REPEAT)
        self.program['u_texture'] = 0

    def render(self):
        self.ctx.clear()
        self.texture.use(location=0)
        self.vao.render()


scene = Scene()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    scene.render()
    pygame.display.flip()

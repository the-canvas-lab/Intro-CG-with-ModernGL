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
pygame.display.set_mode((1600, 1200), flags=pygame.OPENGL | pygame.DOUBLEBUF, vsync=True)


def load_shader(path):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path)) as f:
        return f.read()


def load_texture(ctx, path, filter_mode):
    base = os.path.dirname(os.path.abspath(__file__))
    image = pygame.image.load(os.path.join(base, path)).convert_alpha()
    image = pygame.transform.flip(image, False, True)
    data = pygame.image.tostring(image, 'RGBA')
    texture = ctx.texture(image.get_size(), 4, data)
    # filter is a (minification, magnification) pair.
    # moderngl.NEAREST: pick the single closest texel → sharp, blocky pixels
    # moderngl.LINEAR:  blend the four surrounding texels → smooth result
    #
    # build_mipmaps() is intentionally omitted: it overrides the filter with
    # LINEAR_MIPMAP_LINEAR internally, and mipmaps only apply to minification
    # anyway — this demo uses magnification exclusively.
    texture.filter = (filter_mode, filter_mode)
    return texture


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()

        self.program = self.ctx.program(
            vertex_shader=load_shader('shaders/rect.vert'),
            fragment_shader=load_shader('shaders/rect.frag'),
        )

        # Sample a 10% region centered on the texture (~10× magnification).
        # Left rectangle:  NEAREST — blocky, pixelated look
        # Right rectangle: LINEAR  — smooth, interpolated look
        self.vao_nearest = self._make_rect(-0.95, -0.05, uv_size=0.1, uv_offset=0.5)
        self.vao_linear  = self._make_rect( 0.05,  0.95, uv_size=0.1, uv_offset=0.5)

        self.texture_nearest = load_texture(self.ctx, '../images/europeMap.png', moderngl.NEAREST)
        self.texture_linear  = load_texture(self.ctx, '../images/europeMap.png', moderngl.LINEAR)

        self.program['u_texture'] = 0

    def _make_rect(self, x_min, x_max, uv_size, uv_offset=0.0):
        u0, u1 = uv_offset, uv_offset + uv_size
        vertices = np.array([
            # x       y     z    u   v
            x_max,  0.5,  0.0,  u1, u1,
            x_max, -0.5,  0.0,  u1, u0,
            x_min, -0.5,  0.0,  u0, u0,
            x_min,  0.5,  0.0,  u0, u1,
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

        self.texture_nearest.use(location=0)
        self.vao_nearest.render()

        self.texture_linear.use(location=0)
        self.vao_linear.render()


scene = Scene()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    scene.render()
    pygame.display.flip()

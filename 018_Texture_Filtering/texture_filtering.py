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


def load_texture(ctx, path, filter_mode):
    base = os.path.dirname(os.path.abspath(__file__))
    image = pygame.image.load(os.path.join(base, path)).convert_alpha()
    image = pygame.transform.flip(image, False, True)
    data = pygame.image.tostring(image, 'RGBA')
    texture = ctx.texture(image.get_size(), 4, data)
    # filter is a (minification, magnification) pair.
    # Minification  — texture is smaller than the screen area it covers.
    # Magnification — texture is larger (zoomed in), which is what we see here.
    #
    # moderngl.NEAREST: pick the single closest texel → sharp, blocky pixels
    # moderngl.LINEAR:  blend the four surrounding texels → smooth result
    #
    # Mipmaps are pre-generated half-size copies of the texture used during
    # minification to avoid aliasing artifacts on distant objects.
    # build_mipmaps() generates the full mip chain on the GPU.
    # Mipmap filter modes (e.g. LINEAR_MIPMAP_LINEAR) only apply to the
    # minification filter — magnification never uses mipmaps.
    texture.filter = (filter_mode, filter_mode)
    texture.build_mipmaps()
    return texture


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()

        self.program = self.ctx.program(
            vertex_shader=load_shader('shaders/rect.vert'),
            fragment_shader=load_shader('shaders/rect.frag'),
        )

        # UVs span only 0.0–0.2, so we're magnifying a small region of the
        # texture (~5×) — large enough to see individual texels.
        #
        # Left rectangle:  NEAREST filtering — blocky, pixelated look
        # Right rectangle: LINEAR filtering  — smooth, interpolated look
        self.vao_nearest = self._make_rect(-0.95, -0.05, uv_max=0.2)
        self.vao_linear  = self._make_rect( 0.05,  0.95, uv_max=0.2)

        self.texture_nearest = load_texture(self.ctx, '../images/container.jpg', moderngl.NEAREST)
        self.texture_linear  = load_texture(self.ctx, '../images/container.jpg', moderngl.LINEAR)

        self.program['u_texture'] = 0

    def _make_rect(self, x_min, x_max, uv_max):
        vertices = np.array([
            # x       y     z     u        v
            x_max,  0.5,  0.0,  uv_max,  uv_max,
            x_max, -0.5,  0.0,  uv_max,  0.0,
            x_min, -0.5,  0.0,  0.0,     0.0,
            x_min,  0.5,  0.0,  0.0,     uv_max,
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

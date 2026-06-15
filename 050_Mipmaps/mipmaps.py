# =============================================================================
# Lesson 050 — Mipmaps
# =============================================================================
# Lesson 018 covered MAGNIFICATION (texture too small for the screen area).
# This lesson covers the opposite, MINIFICATION: a distant floor squeezes
# thousands of texels into a single pixel. Sampling just one of them is
# undersampling, and it shimmers ("moiré") as the camera moves.
#
# The fix is the MIP CHAIN: pre-shrunk copies of the texture, each half the
# previous size (256 -> 128 -> 64 -> ... -> 1). Each mip texel already
# AVERAGES many original texels, so sampling the right level replaces the
# shimmer with a clean pre-filtered result. `texture.build_mipmaps()` (used
# silently since lesson 016) generates this chain.
#
# The min-filter then has three parts:  texel filter / MIPMAP / level filter
#
#   LINEAR                  no mipmaps — full shimmer (mode 1)
#   LINEAR_MIPMAP_NEAREST   nearest level — visible bands  (mode 2)
#   LINEAR_MIPMAP_LINEAR    blend 2 levels — "trilinear", smooth (mode 3)
#
# Mode 4 is the X-ray: every mip level is overwritten with a solid color
# (level 0 red, 1 orange, 2 yellow, ...) so you can SEE which level the GPU
# samples at every distance.
#
# Memory cost of the whole chain: only +33%  (1/4 + 1/16 + ... = 1/3).
#
# Vulkan note: there `build_mipmaps()` does not exist — you allocate the
# levels and fill each one yourself with image blits. Knowing what the chain
# IS makes that chapter mechanical instead of mysterious.
#
# Controls:  ← / → — switch filtering mode   Esc — quit
# =============================================================================

import math
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


TEX_SIZE = 256


def make_checker_texture(ctx):
    """A high-frequency checkerboard — the worst case for minification."""
    cells = (np.indices((TEX_SIZE, TEX_SIZE)) // 16).sum(axis=0) % 2
    img = np.where(cells[..., None] == 1,
                   np.uint8(230), np.uint8(25)).repeat(3, axis=2)
    tex = ctx.texture((TEX_SIZE, TEX_SIZE), 3, img.tobytes())
    tex.build_mipmaps()
    return tex


def make_debug_texture(ctx):
    """Same chain, but every level is a solid color: a mip-level X-ray."""
    tex = ctx.texture((TEX_SIZE, TEX_SIZE), 3, b'\x00' * (TEX_SIZE * TEX_SIZE * 3))
    tex.build_mipmaps()  # allocate the full chain, then overwrite each level
    colors = [(255, 0, 0), (255, 128, 0), (255, 255, 0), (0, 200, 0),
              (0, 200, 200), (0, 80, 255), (140, 0, 255), (255, 0, 160),
              (255, 255, 255)]
    for level, color in enumerate(colors):  # 256x256 ... 1x1 = levels 0..8
        size = TEX_SIZE >> level
        data = np.tile(np.array(color, dtype=np.uint8), size * size)
        tex.write(data.tobytes(), level=level)
    return tex


# A long floor strip receding to the horizon, heavily tiled.
FLOOR_VERTS = np.array([
    -20, 0,    2,   0,  0,
     20, 0,    2,  10,  0,
     20, 0, -200,  10, 50,
    -20, 0,    2,   0,  0,
     20, 0, -200,  10, 50,
    -20, 0, -200,   0, 50,
], dtype='f4')


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.program = self.ctx.program(
            vertex_shader=load_shader('shaders/floor.vert'),
            fragment_shader=load_shader('shaders/floor.frag'),
        )
        vbo = self.ctx.buffer(FLOOR_VERTS)
        self.vao = self.ctx.vertex_array(
            self.program, [(vbo, '3f 2f', 'in_position', 'in_uv')])

        self.checker = make_checker_texture(self.ctx)
        self.debug   = make_debug_texture(self.ctx)
        self.program['u_texture'] = 0

        projection = glm.perspective(glm.radians(60.0), 800.0 / 600.0, 0.1, 300.0)
        self.program['projection'].write(projection)

        # (label, texture, (min_filter, mag_filter))
        self.modes = [
            ("1/4  LINEAR, no mipmaps — shimmering moiré",
             self.checker, (moderngl.LINEAR, moderngl.LINEAR)),
            ("2/4  LINEAR_MIPMAP_NEAREST — banded transitions",
             self.checker, (moderngl.LINEAR_MIPMAP_NEAREST, moderngl.LINEAR)),
            ("3/4  LINEAR_MIPMAP_LINEAR — trilinear, smooth",
             self.checker, (moderngl.LINEAR_MIPMAP_LINEAR, moderngl.LINEAR)),
            ("4/4  debug — each color is one mip level",
             self.debug, (moderngl.LINEAR_MIPMAP_NEAREST, moderngl.LINEAR)),
        ]
        self.mode = 0
        self.apply_mode()

    def apply_mode(self):
        label, texture, filt = self.modes[self.mode]
        texture.filter = filt
        texture.use(location=0)
        pygame.display.set_caption(f"050 — Mipmaps   [{label}]   ←/→ to switch")

    def switch(self, step):
        self.mode = (self.mode + step) % len(self.modes)
        self.apply_mode()

    def render(self, t):
        self.ctx.clear(0.05, 0.05, 0.08)

        # Gentle sway: aliasing is most obvious when the camera MOVES.
        eye = glm.vec3(math.sin(t * 0.6) * 1.5, 1.4, 0.0)
        view = glm.lookAt(eye, eye + glm.vec3(0.0, -0.12, -1.0),
                          glm.vec3(0.0, 1.0, 0.0))
        self.program['view'].write(view)
        self.vao.render()


scene = Scene()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_LEFT:
                scene.switch(-1)
            elif event.key == pygame.K_RIGHT:
                scene.switch(+1)

    scene.render(pygame.time.get_ticks() / 1000.0)
    pygame.display.flip()

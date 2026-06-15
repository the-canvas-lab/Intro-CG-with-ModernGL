# =============================================================================
# Lesson 049 — Gamma Correction
# =============================================================================
# Monitors are not linear: a pixel value of 0.5 emits only ~22% of the light
# of a pixel value of 1.0, because displays apply a power curve of roughly
# 2.2 ("gamma"). Two consequences:
#
#   1. All our lighting math so far happened in this warped space, so
#      diffuse falloff and light attenuation never behaved physically.
#   2. Textures painted on a monitor are sRGB-ENCODED — sampling them gives
#      gamma-space values, not light intensities.
#
# The fix has three parts, all visible in floor.frag:
#
#   decode:  tex   = pow(tex, vec3(2.2));        sRGB texture -> linear
#   light:   ...all math in linear space...      (1/d² attenuation now works)
#   encode:  color = pow(color, vec3(1/2.2));    linear -> what the display
#                                                expects, applied ONCE, last
#
# Press SPACE to toggle correction. Watch two things:
#   * the light pools: corrected, the inverse-square falloff looks natural;
#     uncorrected, the same physics looks implausibly dark and harsh
#   * the gradient strip on top: a linear ramp only LOOKS linear when
#     gamma-corrected
#
# In real engines the encode step is free: render into an SRGB framebuffer
# (or, in Vulkan, pick a *_SRGB swapchain format — one of the first choices
# the API forces on you, which is why this lesson exists).
#
# Controls:  Space — toggle gamma correction   Esc — quit
# =============================================================================

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
    data  = pygame.image.tostring(image, 'RGBA')
    tex   = ctx.texture(image.get_size(), 4, data)
    tex.build_mipmaps()
    return tex


# Floor in the XZ plane: pos(3f) normal(3f) uv(2f), tiled 6x6.
S, UV = 12.0, 6.0
FLOOR_VERTS = np.array([
    -S, 0, -S,  0, 1, 0,   0,  0,
     S, 0, -S,  0, 1, 0,  UV,  0,
     S, 0,  S,  0, 1, 0,  UV, UV,
    -S, 0, -S,  0, 1, 0,   0,  0,
     S, 0,  S,  0, 1, 0,  UV, UV,
    -S, 0,  S,  0, 1, 0,   0, UV,
], dtype='f4')

# Unit quad for the gradient strip, centered on the origin.
STRIP_VERTS = np.array([
    -0.5, -0.5,  0.0, 0.0,
     0.5, -0.5,  1.0, 0.0,
     0.5,  0.5,  1.0, 1.0,
    -0.5, -0.5,  0.0, 0.0,
     0.5,  0.5,  1.0, 1.0,
    -0.5,  0.5,  0.0, 1.0,
], dtype='f4')

# Three identical white lights with very different intensities, receding
# into the distance, so falloff differences are impossible to miss.
LIGHT_POSITIONS = [(0.0, 1.0,  6.0), (0.0, 1.0, 0.0), (0.0, 1.0, -6.0)]
LIGHT_COLORS    = [(0.3, 0.3, 0.3), (1.0, 1.0, 1.0), (3.0, 3.0, 3.0)]


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.floor_program = self.ctx.program(
            vertex_shader=load_shader('shaders/floor.vert'),
            fragment_shader=load_shader('shaders/floor.frag'),
        )
        self.strip_program = self.ctx.program(
            vertex_shader=load_shader('shaders/strip.vert'),
            fragment_shader=load_shader('shaders/strip.frag'),
        )

        floor_vbo = self.ctx.buffer(FLOOR_VERTS)
        self.floor_vao = self.ctx.vertex_array(
            self.floor_program,
            [(floor_vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_uv')])

        strip_vbo = self.ctx.buffer(STRIP_VERTS)
        self.strip_vao = self.ctx.vertex_array(
            self.strip_program,
            [(strip_vbo, '2f 2f', 'in_position', 'in_uv')])

        load_texture(self.ctx, '../images/wall.jpg').use(location=0)
        self.floor_program['u_texture'] = 0

        view = glm.lookAt(glm.vec3(0.0, 3.0, 11.0),
                          glm.vec3(0.0, 0.0, 0.0),
                          glm.vec3(0.0, 1.0, 0.0))
        projection = glm.perspective(glm.radians(45.0), 800.0 / 600.0, 0.1, 100.0)
        self.floor_program['view'].write(view)
        self.floor_program['projection'].write(projection)
        self.floor_program['light_positions'].write(
            np.array(LIGHT_POSITIONS, dtype='f4'))
        self.floor_program['light_colors'].write(
            np.array(LIGHT_COLORS, dtype='f4'))

        self.gamma = True
        self.apply_gamma()

    def apply_gamma(self):
        self.floor_program['u_gamma'] = self.gamma
        self.strip_program['u_gamma'] = self.gamma
        state = "ON" if self.gamma else "OFF"
        pygame.display.set_caption(
            f"049 — Gamma Correction [{state}] — Space to toggle")

    def toggle(self):
        self.gamma = not self.gamma
        self.apply_gamma()

    def render(self):
        self.ctx.clear(0.0, 0.0, 0.0)

        self.ctx.enable(moderngl.DEPTH_TEST)
        self.floor_vao.render()

        # Gradient strip overlay along the top edge.
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.strip_program['u_pos']   = (0.0, 0.88)
        self.strip_program['u_scale'] = (1.9, 0.16)
        self.strip_vao.render()


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
            elif event.key == pygame.K_SPACE:
                scene.toggle()

    scene.render()
    pygame.display.flip()

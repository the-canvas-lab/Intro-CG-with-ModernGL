# =============================================================================
# Lesson 040 — Blending (semi-transparent windows)
# =============================================================================
# When a fragment's alpha is less than 1, it should be composited with whatever
# is already behind it in the framebuffer rather than replacing it outright.
# OpenGL handles this automatically once blending is enabled:
#
#   ctx.enable(moderngl.BLEND)
#   ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
#
# The blend equation becomes:
#   result = src_alpha * src_color + (1 − src_alpha) * dst_color
#
# The fragment shader does nothing special — it just outputs the full RGBA
# value from the texture.  The GPU blend unit does the compositing.
#
# RENDER ORDER
# Blending reads from the framebuffer ("dst"), so what's already there matters.
# The rule:
#   1. Draw all opaque geometry first (wall).
#   2. Draw transparent objects back-to-front so that each one composites
#      correctly over everything behind it.
#
# With only two windows the order is trivially hardcoded: back window first,
# then front window.  A general scene with many transparent objects would
# require dynamic sorting, which is why artists usually prefer discard-based
# alpha cutouts (lesson 039) when possible.
#
# Controls:  Esc — quit
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
pygame.display.set_caption("040 — Blending")


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


# Unit quad in the XY plane (-1..1 on each axis).
# Objects are sized and placed using model matrices.
QUAD_VERTS = np.array([
    -1, -1, 0,  0, 0,
     1, -1, 0,  1, 0,
     1,  1, 0,  1, 1,
    -1, -1, 0,  0, 0,
     1,  1, 0,  1, 1,
    -1,  1, 0,  0, 1,
], dtype='f4')


def make_model(pos, scale):
    return glm.scale(glm.translate(glm.mat4(1.0), pos), scale)


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        self.program = self.ctx.program(
            vertex_shader=load_shader('shaders/object.vert'),
            fragment_shader=load_shader('shaders/object.frag'),
        )

        vbo = self.ctx.buffer(QUAD_VERTS)
        self.vao = self.ctx.vertex_array(
            self.program,
            [(vbo, '3f 2f', 'in_position', 'in_uv')],
        )

        self.wall_tex   = load_texture(self.ctx, '../images/wall.jpg')
        self.window_tex = load_texture(self.ctx, '../images/blending_transparent_window.png')
        self.program['u_texture'] = 0

        camera_pos = glm.vec3(0.0, 0.0, 5.0)
        view       = glm.lookAt(camera_pos, glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))
        projection = glm.perspective(glm.radians(45.0), 800.0 / 600.0, 0.1, 100.0)
        self.program['view'].write(view)
        self.program['projection'].write(projection)

        self.wall_model = make_model(glm.vec3(0.0, 0.0, -5.0), glm.vec3(8.0, 6.0, 1.0))

        # Windows are listed back-to-front so they are drawn in that order.
        # Both are the same landscape size; offset horizontally so they partially overlap.
        WIN = glm.vec3(1.2, 0.8, 1.0)
        self.window_models = [
            make_model(glm.vec3(-0.75, 0.0, -2.0), WIN),  # back,  shifted left
            make_model(glm.vec3( 0.75, 0.0,  0.0), WIN),  # front, shifted right
        ]

    def render(self):
        self.ctx.clear(0.1, 0.1, 0.1)

        # 1. Opaque geometry first so transparent objects have something to blend against.
        self.wall_tex.use(location=0)
        self.program['model'].write(self.wall_model)
        self.vao.render()

        # 2. Transparent windows back-to-front.
        self.window_tex.use(location=0)
        for model in self.window_models:
            self.program['model'].write(model)
            self.vao.render()


scene = Scene()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

    scene.render()
    pygame.display.flip()

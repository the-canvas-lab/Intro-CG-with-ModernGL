# =============================================================================
# Lesson 039 — Discarding Fragments
# =============================================================================
# Grass sprites use an RGBA texture where the background is fully transparent.
# Without special handling, the GPU would write those transparent pixels to the
# color buffer and produce ugly black or white rectangles around each blade.
#
# The fix is a single line in the fragment shader:
#
#   if (tex_color.a < 0.1) discard;
#
# 'discard' exits the fragment shader immediately — no color write, no depth
# write.  The fragment simply does not exist as far as the pipeline is concerned.
# Because the depth buffer is untouched, objects behind the transparent region
# are revealed correctly without any need to sort geometry by depth.
#
# This technique is called "alpha cutout" or "alpha testing" and is the
# standard approach for vegetation, fences, and similar hard-edged transparency.
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
pygame.display.set_caption("039 — Discarding Fragments")


def load_shader(path):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path)) as f:
        return f.read()


def load_texture(ctx, path):
    base = os.path.dirname(os.path.abspath(__file__))
    image = pygame.image.load(os.path.join(base, path)).convert_alpha()
    image = pygame.transform.flip(image, False, True)
    data  = pygame.image.tostring(image, 'RGBA')
    tex   = ctx.texture(image.get_size(), 4, data)
    tex.build_mipmaps()
    return tex


# Large floor quad in the XZ plane.  Dummy UVs are included so it can share
# the same vertex shader as the grass quads.
FLOOR_VERTS = np.array([
    -10, 0, -10,  0, 0,
     10, 0, -10,  1, 0,
     10, 0,  10,  1, 1,
    -10, 0, -10,  0, 0,
     10, 0,  10,  1, 1,
    -10, 0,  10,  0, 1,
], dtype='f4')

# Unit grass quad: 1 wide, 1 tall, base at y = 0, facing +z.
# Each blade is placed in the world via a translation matrix.
GRASS_VERTS = np.array([
    -0.5, 0.0, 0.0,  0.0, 0.0,
     0.5, 0.0, 0.0,  1.0, 0.0,
     0.5, 1.0, 0.0,  1.0, 1.0,
    -0.5, 0.0, 0.0,  0.0, 0.0,
     0.5, 1.0, 0.0,  1.0, 1.0,
    -0.5, 1.0, 0.0,  0.0, 1.0,
], dtype='f4')

GRASS_POSITIONS = [
    glm.vec3( 0.0, 0.0,  0.0),
    glm.vec3(-1.5, 0.0, -0.5),
    glm.vec3( 1.5, 0.0,  0.5),
    glm.vec3(-0.3, 0.0, -2.3),
    glm.vec3( 0.5, 0.0, -0.6),
    glm.vec3(-2.0, 0.0,  0.3),
    glm.vec3( 2.0, 0.0, -0.3),
    glm.vec3(-1.0, 0.0, -1.5),
    glm.vec3( 1.0, 0.0,  1.2),
    glm.vec3( 0.0, 0.0, -3.0),
]


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)

        vert = load_shader('shaders/object.vert')
        self.floor_program = self.ctx.program(
            vertex_shader=vert,
            fragment_shader=load_shader('shaders/floor.frag'),
        )
        self.grass_program = self.ctx.program(
            vertex_shader=vert,
            fragment_shader=load_shader('shaders/grass.frag'),
        )

        floor_vbo = self.ctx.buffer(FLOOR_VERTS)
        self.floor_vao = self.ctx.vertex_array(
            self.floor_program,
            [(floor_vbo, '3f 2f', 'in_position', 'in_uv')],
        )

        grass_vbo = self.ctx.buffer(GRASS_VERTS)
        self.grass_vao = self.ctx.vertex_array(
            self.grass_program,
            [(grass_vbo, '3f 2f', 'in_position', 'in_uv')],
        )

        grass_tex = load_texture(self.ctx, '../images/grass.png')
        # Clamp to edge so UV coordinates that land on the border due to
        # floating-point imprecision don't bleed in a non-transparent texel.
        grass_tex.repeat_x = False
        grass_tex.repeat_y = False
        grass_tex.use(location=0)
        self.grass_program['u_texture'] = 0

        camera_pos = glm.vec3(0.0, 1.5, 5.0)
        view       = glm.lookAt(camera_pos, glm.vec3(0.0, 0.5, 0.0), glm.vec3(0.0, 1.0, 0.0))
        projection = glm.perspective(glm.radians(45.0), 800.0 / 600.0, 0.1, 100.0)

        for prog in (self.floor_program, self.grass_program):
            prog['view'].write(view)
            prog['projection'].write(projection)

        self.grass_models = [glm.translate(glm.mat4(1.0), p) for p in GRASS_POSITIONS]

    def render(self):
        self.ctx.clear(0.1, 0.1, 0.1)

        self.floor_program['model'].write(glm.mat4(1.0))
        self.floor_vao.render()

        for model in self.grass_models:
            self.grass_program['model'].write(model)
            self.grass_vao.render()


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

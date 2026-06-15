# =============================================================================
# Lesson 045 — Instancing
# =============================================================================
# Without instancing, drawing N copies of a mesh requires N separate draw
# calls.  Each call carries CPU-side overhead (uniform upload, buffer binding,
# driver validation) that quickly becomes the bottleneck when N is large —
# typically above a few thousand objects per frame.
#
# Instancing collapses N draw calls into one.  Per-instance data (transforms,
# colours, etc.) lives in a vertex buffer whose attribute *divisor* is set to
# 1, meaning the GPU advances one element per *instance* rather than per
# vertex.  A single call then renders all N copies.
#
#   vao.render(instances=N)
#
# In the vertex array format string the '/i' suffix marks a per-instance
# binding:
#
#   (inst_vbo, '2f 3f /i', 'in_offset', 'in_color')
#
# The built-in gl_InstanceID integer identifies the current instance and can
# be used inside the shader when no per-instance buffer is needed.
#
# This lesson renders 100 coloured 2D quads in a 10×10 grid — all in a single
# draw call.  Per-instance data: vec2 offset + vec3 color.
#
# Controls:  Esc — quit
# =============================================================================

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
pygame.display.set_caption("045 — Instancing  (100 quads, 1 draw call)")

# Unit quad in NDC — will be scaled and offset per instance.
QUAD_VERTS = np.array([
    -0.5, -0.5,
     0.5, -0.5,
     0.5,  0.5,
    -0.5, -0.5,
     0.5,  0.5,
    -0.5,  0.5,
], dtype='f4')


def load_shader(path):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path), encoding='utf-8') as f:
        return f.read()


def build_quad_instances():
    """100 instances: vec2 offset + vec3 color, interleaved."""
    offsets, colors = [], []
    for y in range(10):
        for x in range(10):
            offsets.append([-0.9 + x * 0.2, -0.9 + y * 0.2])
            colors.append([x / 9.0, y / 9.0, 0.5])
    data = np.hstack([
        np.array(offsets, dtype='f4'),
        np.array(colors,  dtype='f4'),
    ]).astype('f4')
    return data.tobytes()


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()

        self.prog = self.ctx.program(
            vertex_shader=load_shader('shaders/quad.vert'),
            fragment_shader=load_shader('shaders/quad.frag'),
        )
        quad_vbo      = self.ctx.buffer(QUAD_VERTS.tobytes())
        quad_inst_vbo = self.ctx.buffer(build_quad_instances())
        self.vao = self.ctx.vertex_array(
            self.prog,
            [
                (quad_vbo,      '2f',       'in_position'),
                (quad_inst_vbo, '2f 3f /i', 'in_offset', 'in_color'),
            ],
        )

    def render(self):
        self.ctx.clear(0.05, 0.05, 0.08)
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.vao.render(instances=100)


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

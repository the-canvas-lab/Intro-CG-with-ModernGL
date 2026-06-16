# =============================================================================
# Lesson 048 — Uniform Buffer Objects
# =============================================================================
# So far every uniform was set one by one, per program:
#
#     prog_a['view'].write(view)
#     prog_b['view'].write(view)      # ...same data, uploaded again
#
# A Uniform Buffer Object (UBO) stores uniforms in a regular GPU buffer that
# any number of shader programs can read through a shared *binding point*:
#
#     buffer  --bound to-->  binding point 0  <--read by--  program A
#                                             <--read by--  program B
#
# Write the buffer ONCE per frame and every program sees the new values.
# This is how engines share camera matrices, lights, and time across dozens
# of shaders — and it is the conceptual twin of what Vulkan calls a uniform
# buffer accessed through a descriptor set. In Vulkan there are NO loose
# uniforms at all; everything works the way this lesson works.
#
# The catch is memory layout: the GLSL block is declared `std140`, a fixed
# layout where e.g. a vec3 is padded to 16 bytes. The CPU must write bytes
# that match — see the padded numpy array in render().
#
# Scene: four cubes, alternating between two shader programs (diffuse /
# emissive). Camera matrices and the animated light live in two UBOs that
# are written once per frame, yet drive both programs.
#
# Controls:  Esc — quit
# =============================================================================

import math
import os
import sys

import glm
import moderngl
import numpy as np
import pygame
import pywavefront

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
pygame.display.set_caption("048 — Uniform Buffer Objects")


def load_shader(path):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path), encoding='utf-8') as f:
        return f.read()


def load_obj_mesh(path):
    base = os.path.dirname(os.path.abspath(__file__))
    scene = pywavefront.Wavefront(
        os.path.join(base, path), create_materials=True, parse=True,
    )
    all_verts = []
    for mat in scene.materials.values():
        if mat.vertices:
            all_verts.extend(mat.vertices)
    verts = np.array(all_verts, dtype='f4').reshape(-1, 8)
    return np.ascontiguousarray(np.hstack([verts[:, 5:], verts[:, 2:5], verts[:, 0:2]]))


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)

        vert = load_shader('shaders/object.vert')
        self.prog_diffuse = self.ctx.program(
            vertex_shader=vert, fragment_shader=load_shader('shaders/diffuse.frag'))
        self.prog_emissive = self.ctx.program(
            vertex_shader=vert, fragment_shader=load_shader('shaders/emissive.frag'))

        # The mesh has pos(3f) normal(3f) uv(2f); diffuse uses normals, emissive
        # does not — skip those bytes with padding so active attributes match.
        vbo = self.ctx.buffer(load_obj_mesh('../models/cube.obj'))
        self.vaos = [
            self.ctx.vertex_array(
                self.prog_diffuse, [(vbo, '3f 3f 2x4', 'in_position', 'in_normal')]),
            self.ctx.vertex_array(
                self.prog_emissive,   [(vbo, '3f 12x 2x4', 'in_position')]),
        ]

        # --- the actual lesson -----------------------------------------------
        # 1. Tell each program which binding point its blocks read from.
        for prog in (self.prog_diffuse, self.prog_emissive):
            prog['Matrices'].binding   = 0
            prog['LightBlock'].binding = 1

        # 2. Create the buffers and attach them to those binding points.
        #    Matrices: two mat4 = 2 x 64 bytes. LightBlock: two padded
        #    vec3 = 2 x 16 bytes (std140!).
        self.matrices_ubo = self.ctx.buffer(reserve=128)
        self.light_ubo    = self.ctx.buffer(reserve=32)
        self.matrices_ubo.bind_to_uniform_block(0)
        self.light_ubo.bind_to_uniform_block(1)

        # 3. The projection never changes: write its 64 bytes once, at its
        #    std140 offset inside the block.
        projection = glm.perspective(glm.radians(45.0), 800.0 / 600.0, 0.1, 100.0)
        self.matrices_ubo.write(projection, offset=64)

        self.cube_xs = [-4.5, -1.5, 1.5, 4.5]

    def render(self, t):
        self.ctx.clear(0.05, 0.05, 0.08)

        # One write updates the camera for BOTH programs — compare with
        # earlier lessons that looped over programs uploading 'view' twice.
        eye  = glm.vec3(math.sin(t * 0.4) * 8.0, 3.0, math.cos(t * 0.4) * 8.0)
        view = glm.lookAt(eye, glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))
        self.matrices_ubo.write(view, offset=0)

        # std140 layout by hand: each vec3 occupies a 16-byte slot, so a
        # 0.0 pad float follows each one. Forgetting the padding is THE
        # classic UBO bug — colors silently read shifted garbage.
        light_dir   = glm.normalize(glm.vec3(-0.4, -1.0, -0.3))
        # Hue drifts but every channel stays >= 0.3 so both cube styles
        # remain visible at every phase.
        light_color = glm.vec3(0.65) + 0.35 * glm.vec3(
            math.sin(t), math.sin(t + 2.1), math.sin(t + 4.2))
        self.light_ubo.write(np.array([
            light_dir.x,   light_dir.y,   light_dir.z,   0.0,   # vec3 + pad
            light_color.x, light_color.y, light_color.z, 0.0,   # vec3 + pad
        ], dtype='f4'))

        # 'model' stays a per-object plain uniform — it differs per draw, so
        # a shared buffer would buy nothing.
        for i, x in enumerate(self.cube_xs):
            model = glm.translate(glm.mat4(1.0), glm.vec3(x, 0.0, 0.0))
            model = glm.rotate(model, t * 0.7 + i, glm.vec3(0.0, 1.0, 0.0))
            prog  = (self.prog_diffuse, self.prog_emissive)[i % 2]
            prog['model'].write(model)
            self.vaos[i % 2].render()


scene = Scene()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

    scene.render(pygame.time.get_ticks() / 1000.0)
    pygame.display.flip()

# =============================================================================
# Exercise 035 — Emission Map
# =============================================================================
# An emission map lets a surface emit light on its own, regardless of any
# lamp in the scene.  Every texel in the emission map is simply added to the
# final fragment color — it is not affected by the light position or the
# surface normal.
#
# The scene is identical to lesson 034 (Lighting Maps).  Your task is to
# extend the material struct and the Phong calculation in the fragment shader
# so that container2_emission.png appears as a glowing overlay on the container.
#
# Tasks (all changes are in shaders/object.frag):
#
#   TODO 1 — Add a sampler2D emission field to the Material struct.
#
#   TODO 2 — Sample the emission texture and add it to the final color.
#             The emission contribution is independent of the lamp.
#
# In exercise_emission_map.py (this file):
#
#   TODO 3 — Load container2_emission.png, bind it to unit 2, and set material.emission = 2.
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
pygame.display.set_caption("035 — Emission Map (exercise)")


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


def load_obj_mesh(path):
    base = os.path.dirname(os.path.abspath(__file__))
    scene = pywavefront.Wavefront(
        os.path.join(base, path),
        create_materials=True,
        parse=True,
    )
    all_verts = []
    for material in scene.materials.values():
        if material.vertices:
            all_verts.extend(material.vertices)
    verts = np.array(all_verts, dtype='f4').reshape(-1, 8)
    pos = verts[:, 5:]
    nrm = verts[:, 2:5]
    uv  = verts[:, 0:2]
    return np.ascontiguousarray(np.hstack([pos, nrm, uv]))


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.object_program = self.ctx.program(
            vertex_shader=load_shader('shaders/object.vert'),
            fragment_shader=load_shader('shaders/object.frag'),
        )
        self.lamp_program = self.ctx.program(
            vertex_shader=load_shader('shaders/lamp.vert'),
            fragment_shader=load_shader('shaders/lamp.frag'),
        )

        self.vbo = self.ctx.buffer(load_obj_mesh('../models/cube.obj'))
        self.object_vao = self.ctx.vertex_array(
            self.object_program,
            [(self.vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_uv')],
        )
        self.lamp_vao = self.ctx.vertex_array(
            self.lamp_program, [(self.vbo, '3f 20x', 'in_position')]
        )

        self.diffuse_tex  = load_texture(self.ctx, '../images/container2.png')
        self.specular_tex = load_texture(self.ctx, '../images/container2_specular.png')
        # TODO 3 — load container2_emission.png and bind it to unit 2

        self.diffuse_tex.use(location=0)
        self.specular_tex.use(location=1)

        self.camera_pos = glm.vec3(0.0, 4.0, -6.0)
        view       = glm.lookAt(self.camera_pos, glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))
        projection = glm.perspective(glm.radians(40.0), 800.0 / 600.0, 0.1, 100.0)

        for prog in (self.object_program, self.lamp_program):
            prog['view'].write(view)
            prog['projection'].write(projection)

        self.object_program['material.diffuse']   = 0
        self.object_program['material.specular']  = 1
        # TODO 3 (continued) — tell the shader which unit holds the emission map
        self.object_program['material.shininess'] = 64.0

        self.object_program['light.ambient']  = (0.2, 0.2, 0.2)
        self.object_program['light.diffuse']  = (0.5, 0.5, 0.5)
        self.object_program['light.specular'] = (1.0, 1.0, 1.0)
        self.object_program['u_view_pos']     = tuple(self.camera_pos)

        model         = glm.rotate(glm.mat4(1.0), glm.radians(290.0), glm.vec3(0.5, 1.0, 0.0))
        normal_matrix = glm.mat3(glm.transpose(glm.inverse(model)))
        self.object_program['model'].write(model)
        self.object_program['normal_matrix'].write(normal_matrix)

    def render(self, time):
        self.ctx.clear(0.1, 0.1, 0.1)

        light_pos = glm.vec3(math.cos(time * 2.0), 2.0, math.sin(time * 2.0))
        self.object_program['light.position'] = tuple(light_pos)
        self.object_vao.render()

        lamp_model = glm.scale(glm.translate(glm.mat4(1.0), light_pos), glm.vec3(0.2))
        self.lamp_program['model'].write(lamp_model)
        self.lamp_vao.render()


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

    scene.render(pygame.time.get_ticks() / 1000.0)
    pygame.display.flip()

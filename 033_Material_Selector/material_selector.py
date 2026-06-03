# =============================================================================
# Lesson 033 — Material Selector
# =============================================================================
# Extends lesson 032 by preloading an array of Material structs to the GPU
# and selecting the active one with a single integer uniform.
#
# New concepts
# ------------
# Uniform arrays
#   GLSL lets you declare arrays of structs:
#       uniform Material materials[8];
#   All 8 materials are uploaded once at startup.  Switching materials only
#   requires updating a single integer uniform — no struct re-upload per frame.
#
# Dynamic array indexing
#   The fragment shader indexes into the array with a non-constant uniform:
#       Material mat = materials[u_material_index];
#   This is allowed in GLSL 3.30 (OpenGL 3.3 core).
#
# Integer uniform
#   moderngl uploads Python ints to GLSL `uniform int` the same way as floats:
#       program['u_material_index'] = 3
#
# Controls:  ← / → — cycle through materials   Esc — quit
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


def load_shader(path):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path)) as f:
        return f.read()


def load_obj_positions_normals(path):
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
    return np.ascontiguousarray(np.hstack([pos, nrm]))


# fmt: off
# Material presets from http://devernay.free.fr/cours/opengl/materials.html
MATERIALS = [
    ("Emerald",      dict(ambient=(0.0215,   0.1745,   0.0215),   diffuse=(0.07568,  0.61424,  0.07568),  specular=(0.633,     0.727811, 0.633),     shininess=76.8)),
    ("Gold",         dict(ambient=(0.24725,  0.1995,   0.0745),   diffuse=(0.75164,  0.60648,  0.22648),  specular=(0.628281,  0.555802, 0.366065),  shininess=51.2)),
    ("Ruby",         dict(ambient=(0.1745,   0.01175,  0.01175),  diffuse=(0.61424,  0.04136,  0.04136),  specular=(0.727811,  0.626959, 0.626959),  shininess=76.8)),
    ("Pearl",        dict(ambient=(0.25,     0.20725,  0.20725),  diffuse=(1.0,      0.829,    0.829),    specular=(0.296648,  0.296648, 0.296648),  shininess=11.264)),
    ("Obsidian",     dict(ambient=(0.05375,  0.05,     0.06625),  diffuse=(0.18275,  0.17,     0.22525),  specular=(0.332741,  0.328634, 0.346435),  shininess=38.4)),
    ("Chrome",       dict(ambient=(0.25,     0.25,     0.25),     diffuse=(0.4,      0.4,      0.4),      specular=(0.774597,  0.774597, 0.774597),  shininess=76.8)),
    ("Bronze",       dict(ambient=(0.2125,   0.1275,   0.054),    diffuse=(0.714,    0.4284,   0.18144),  specular=(0.393548,  0.271906, 0.166721),  shininess=25.6)),
    ("Cyan Plastic", dict(ambient=(0.0,      0.1,      0.06),     diffuse=(0.0,      0.50980,  0.50980),  specular=(0.50196,   0.50196,  0.50196),   shininess=32.0)),
]
# fmt: on


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

        self.vbo = self.ctx.buffer(load_obj_positions_normals('../models/cube.obj'))
        self.object_vao = self.ctx.vertex_array(
            self.object_program, [(self.vbo, '3f 3f', 'in_position', 'in_normal')]
        )
        self.lamp_vao = self.ctx.vertex_array(
            self.lamp_program, [(self.vbo, '3f 12x', 'in_position')]
        )

        camera_pos = glm.vec3(0.0, 4.0, -6.0)
        view       = glm.lookAt(camera_pos, glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))
        projection = glm.perspective(glm.radians(40.0), 800.0 / 600.0, 0.1, 100.0)

        for prog in (self.object_program, self.lamp_program):
            prog['view'].write(view)
            prog['projection'].write(projection)

        # Upload all materials to the GPU array once at startup.
        # Each element is addressed by its index: 'materials[i].field'.
        for i, (_, mat) in enumerate(MATERIALS):
            self.object_program[f'materials[{i}].ambient']   = mat['ambient']
            self.object_program[f'materials[{i}].diffuse']   = mat['diffuse']
            self.object_program[f'materials[{i}].specular']  = mat['specular']
            self.object_program[f'materials[{i}].shininess'] = mat['shininess']

        self.object_program['light.ambient']  = (0.2, 0.2, 0.2)
        self.object_program['light.diffuse']  = (0.5, 0.5, 0.5)
        self.object_program['light.specular'] = (1.0, 1.0, 1.0)
        self.object_program['u_view_pos']     = tuple(camera_pos)

        self.material_index = 0
        self._apply_material()

    def _apply_material(self):
        self.object_program['u_material_index'] = self.material_index
        name = MATERIALS[self.material_index][0]
        n    = len(MATERIALS)
        pygame.display.set_caption(
            f"033 — Material Selector  [{self.material_index + 1}/{n}] {name}  (← →)"
        )

    def select_material(self, delta):
        self.material_index = (self.material_index + delta) % len(MATERIALS)
        self._apply_material()

    def render(self, time):
        self.ctx.clear(0.1, 0.1, 0.1)

        light_pos     = glm.vec3(0.9, 2.0, 0)
        model         = glm.rotate(glm.mat4(1.0), glm.radians(290.0), glm.vec3(0.5, 1.0, 0.0))
        
        normal_matrix = glm.mat3(glm.transpose(glm.inverse(model)))

        self.object_program['model'].write(model)
        self.object_program['normal_matrix'].write(normal_matrix)
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
            elif event.key == pygame.K_RIGHT:
                scene.select_material(+1)
            elif event.key == pygame.K_LEFT:
                scene.select_material(-1)

    scene.render(pygame.time.get_ticks() / 1000.0)
    pygame.display.flip()

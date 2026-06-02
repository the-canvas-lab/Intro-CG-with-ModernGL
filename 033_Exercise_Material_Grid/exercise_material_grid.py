# =============================================================================
# Exercise 033 — Material Grid
# =============================================================================
# Starting point: lesson 032 (Material Selector).
#
# Instead of displaying one material at a time, render all 8 materials
# simultaneously as a 4×2 grid of cubes so they can be compared side by side.
#
# The key insight: you can change a uniform between draw calls to render the
# same geometry with a different appearance each time.
#
# Tasks (all in render())
# -----------------------
# 1. Compute each cube's grid position from its index i:
#        col = i % COLS
#        row = i // COLS
#        x   = (col - (COLS - 1) / 2.0) * SPACING   ← centers the column
#        y   = (row - (ROWS - 1) / 2.0) * SPACING   ← centers the row
#
# 2. Build the model matrix — translate the shared rotation to (x, y, 0):
#        model = glm.translate(glm.mat4(1.0), glm.vec3(x, y, 0.0)) * SHARED_ROTATION
#    This rotates each cube in place first, then moves it to its grid cell.
#
# 3. Select the material before drawing:
#        self.object_program['u_material_index'] = i
#
# 4. Upload model and render:
#        self.object_program['model'].write(model)
#        self.object_vao.render()
#
# The normal matrix is the same for every cube (same rotation) — upload it
# once before the loop, not inside it.
# =============================================================================

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
pygame.display.set_caption("033 — Material Grid")


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

COLS    = 4
ROWS    = 2
SPACING = 2.5
LAMP_POS = glm.vec3(0.0, 5.0, -2.0)

# All cubes share the same rotation so multiple faces are visible.
# Pre-compute both the model rotation and its normal matrix — they never change.
SHARED_ROTATION      = glm.rotate(glm.mat4(1.0), glm.radians(25.0), glm.vec3(0.3, 1.0, 0.2))
SHARED_NORMAL_MATRIX = glm.mat3(glm.transpose(glm.inverse(SHARED_ROTATION)))


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

        camera_pos = glm.vec3(0.0, 0.5, -11.0)
        view       = glm.lookAt(camera_pos, glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))
        projection = glm.perspective(glm.radians(50.0), 800.0 / 600.0, 0.1, 100.0)

        for prog in (self.object_program, self.lamp_program):
            prog['view'].write(view)
            prog['projection'].write(projection)

        for i, (_, mat) in enumerate(MATERIALS):
            self.object_program[f'materials[{i}].ambient']   = mat['ambient']
            self.object_program[f'materials[{i}].diffuse']   = mat['diffuse']
            self.object_program[f'materials[{i}].specular']  = mat['specular']
            self.object_program[f'materials[{i}].shininess'] = mat['shininess']

        self.object_program['light.position'] = tuple(LAMP_POS)
        self.object_program['light.ambient']  = (0.2, 0.2, 0.2)
        self.object_program['light.diffuse']  = (0.7, 0.7, 0.7)
        self.object_program['light.specular'] = (1.0, 1.0, 1.0)
        self.object_program['u_view_pos']     = tuple(camera_pos)

    def render(self, time):
        self.ctx.clear(0.1, 0.1, 0.1)

        # Normal matrix is the same for all cubes — upload once before the loop.
        self.object_program['normal_matrix'].write(SHARED_NORMAL_MATRIX)

        for i in range(len(MATERIALS)):
            # TODO: compute col, row, x, y from i using COLS, ROWS, SPACING
            # TODO: model = glm.translate(glm.mat4(1.0), glm.vec3(x, y, 0.0)) * SHARED_ROTATION
            # TODO: self.object_program['u_material_index'] = i
            # TODO: self.object_program['model'].write(model)
            # TODO: self.object_vao.render()
            pass

        lamp_model = glm.scale(glm.translate(glm.mat4(1.0), LAMP_POS), glm.vec3(0.2))
        self.lamp_program['model'].write(lamp_model)
        self.lamp_vao.render()


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

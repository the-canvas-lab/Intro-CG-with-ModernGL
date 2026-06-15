# =============================================================================
# Exercise 031 — Gouraud Shading (split-screen comparison)
# =============================================================================
# The 800×600 window is split into two equal panels:
#
#   Left  — Phong shading   (per-fragment, provided as reference)
#   Right — Gouraud shading (per-vertex,   your TODO)
#
# Phong: the lighting equation is evaluated once per fragment — accurate.
# Gouraud: the lighting equation is evaluated once per vertex and the GPU
#   interpolates the result across the triangle — cheaper, but specular
#   highlights appear banded or shift abruptly at face edges.
#
# TODO: implement shaders/gouraud_object.vert and shaders/gouraud_object.frag
#       until the right panel shows correct lighting, then compare the specular
#       highlight on both sides as the lamp orbits.
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
pygame.display.set_caption("031 — Left: Phong (reference)  |  Right: Gouraud (TODO)")


def load_shader(path):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path), encoding='utf-8') as f:
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


HALF_W = 400
H      = 600


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.phong_program = self.ctx.program(
            vertex_shader=load_shader('shaders/phong_object.vert'),
            fragment_shader=load_shader('shaders/phong_object.frag'),
        )
        self.gouraud_program = self.ctx.program(
            vertex_shader=load_shader('shaders/gouraud_object.vert'),
            fragment_shader=load_shader('shaders/gouraud_object.frag'),
        )
        self.lamp_program = self.ctx.program(
            vertex_shader=load_shader('shaders/lamp.vert'),
            fragment_shader=load_shader('shaders/lamp.frag'),
        )

        self.vbo = self.ctx.buffer(load_obj_positions_normals('../models/cube.obj'))
        self.phong_object_vao = self.ctx.vertex_array(
            self.phong_program, [(self.vbo, '3f 3f', 'in_position', 'in_normal')]
        )
        self.gouraud_object_vao = self.ctx.vertex_array(
            self.gouraud_program, [(self.vbo, '3f 3f', 'in_position', 'in_normal')]
        )
        self.lamp_vao = self.ctx.vertex_array(
            self.lamp_program, [(self.vbo, '3f 12x', 'in_position')]
        )

        camera_pos = glm.vec3(0.0, 4.0, -6.0)
        view       = glm.lookAt(camera_pos, glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))
        # Each panel is 400×600 — use that aspect ratio so neither side is distorted.
        projection = glm.perspective(glm.radians(40.0), HALF_W / H, 0.1, 100.0)

        for prog in (self.phong_program, self.gouraud_program, self.lamp_program):
            prog['view'].write(view)
            prog['projection'].write(projection)

        for prog in (self.phong_program, self.gouraud_program):
            prog['u_object_color'] = (1.0, 0.5, 0.31)  # coral
            prog['u_light_color']  = (1.0, 1.0, 1.0)
            prog['u_view_pos']     = tuple(camera_pos)

    def _render_panel(self, x, object_vao, object_prog, model, normal_matrix, light_pos, lamp_model):
        # Restrict clear and rendering to this panel's half of the screen.
        self.ctx.scissor  = (x, 0, HALF_W, H)
        self.ctx.viewport = (x, 0, HALF_W, H)
        self.ctx.clear(0.1, 0.1, 0.1)

        object_prog['model'].write(model)
        object_prog['normal_matrix'].write(normal_matrix)
        object_prog['u_light_pos'] = tuple(light_pos)
        object_vao.render()

        self.lamp_program['model'].write(lamp_model)
        self.lamp_vao.render()

    def render(self, time):
        light_pos     = glm.vec3(0.9, 2.0, -0.6)
        model         = glm.rotate(glm.mat4(1.0), glm.radians(300.0), glm.vec3(0.5, 1.0, 0.0))
        normal_matrix = glm.mat3(glm.transpose(glm.inverse(model)))
        lamp_model    = glm.scale(glm.translate(glm.mat4(1.0), light_pos), glm.vec3(0.2))

        self._render_panel(0,      self.phong_object_vao,   self.phong_program,   model, normal_matrix, light_pos, lamp_model)
        self._render_panel(HALF_W, self.gouraud_object_vao, self.gouraud_program, model, normal_matrix, light_pos, lamp_model)

        # 2-pixel wide divider between the panels.
        self.ctx.scissor = (HALF_W - 1, 0, 2, H)
        self.ctx.clear(0.4, 0.4, 0.4)


scene = Scene()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    scene.render(pygame.time.get_ticks() / 1000.0)
    pygame.display.flip()

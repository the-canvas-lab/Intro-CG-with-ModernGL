# =============================================================================
# Lesson 030 — Phong Component Decomposition
# =============================================================================
# The Phong model sums three terms: ambient + diffuse + specular.
# Use arrow keys to cycle through four rendering modes and inspect each
# component in isolation before seeing the full result.
#
#   0 — Ambient only   flat, view-independent base light
#   1 — Diffuse only   shading that follows the lamp's position
#   2 — Specular only  the highlight — watch it move as the lamp orbits
#   3 — Full Phong     all three summed
#
# Controls:  ← / → — switch mode   Esc — quit
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


MODES = ["Ambient", "Diffuse", "Specular", "Full (Phong)"]

# Chrome: neutral grey makes the shape of each component clearly visible.
MATERIAL = dict(
    ambient=(0.25, 0.25, 0.25),
    diffuse=(0.4,  0.4,  0.4),
    specular=(0.774597, 0.774597, 0.774597),
    shininess=76.8,
)


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

        self.camera_pos = glm.vec3(0.0, 4.0, -6.0)
        view       = glm.lookAt(self.camera_pos, glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))
        projection = glm.perspective(glm.radians(40.0), 800.0 / 600.0, 0.1, 100.0)

        for prog in (self.object_program, self.lamp_program):
            prog['view'].write(view)
            prog['projection'].write(projection)

        m = MATERIAL
        self.object_program['material.ambient']   = m['ambient']
        self.object_program['material.diffuse']   = m['diffuse']
        self.object_program['material.specular']  = m['specular']
        self.object_program['material.shininess'] = m['shininess']

        self.object_program['light.ambient']  = (0.3, 0.3, 0.3)
        self.object_program['light.diffuse']  = (1.0, 1.0, 1.0)
        self.object_program['light.specular'] = (1.0, 1.0, 1.0)
        self.object_program['u_view_pos']     = tuple(self.camera_pos)

        self.mode = 0
        self._apply_mode()

    def _apply_mode(self):
        self.object_program['u_mode'] = self.mode
        label = MODES[self.mode]
        pygame.display.set_caption(
            f"030 — Phong Components  [{self.mode + 1}/{len(MODES)}] {label}  (← →)"
        )
        print(f"[{self.mode + 1}/{len(MODES)}] {label}")

    def select_mode(self, delta):
        self.mode = (self.mode + delta) % len(MODES)
        self._apply_mode()

    def render(self, time):
        self.ctx.clear(0.1, 0.1, 0.1)

        light_pos = glm.vec3(math.cos(time * 2.0), 2.0, math.sin(time * 2.0))
        
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
                scene.select_mode(+1)
            elif event.key == pygame.K_LEFT:
                scene.select_mode(-1)

    scene.render(pygame.time.get_ticks() / 1000.0)
    pygame.display.flip()

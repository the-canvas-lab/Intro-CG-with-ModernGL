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
    # pywavefront produces T2F_N3F_V3F: [u, v, nx, ny, nz, x, y, z] per vertex.
    # Rearrange to [x, y, z, nx, ny, nz] so the VAO can use '3f 3f' with
    # ('in_position', 'in_normal') and '3f 12x' for the position-only lamp.
    all_verts = []
    for material in scene.materials.values():
        if material.vertices:
            all_verts.extend(material.vertices)
    verts = np.array(all_verts, dtype='f4').reshape(-1, 8)
    pos = verts[:, 5:]    # x y z
    nrm = verts[:, 2:5]   # nx ny nz
    return np.ascontiguousarray(np.hstack([pos, nrm]))


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

        # Object VAO reads both position and normal from the interleaved buffer.
        # Lamp VAO only reads position — it uses a separate shader with no lighting.
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

        self.object_program['u_object_color'] = (1.0, 0.5, 0.31)
        self.object_program['u_light_color']  = (1.0, 1.0, 1.0)
        # Camera position is needed for the specular highlight calculation.
        # It stays constant here — lighting in view space is covered in exercises.
        self.object_program['u_view_pos'] = tuple(self.camera_pos)

    def render(self, time):
        self.ctx.clear(0.1, 0.1, 0.1)

        light_pos = glm.vec3(1.0 * math.cos(time), 2.0, 1.0 * math.sin(time))

        model = glm.rotate(glm.mat4(1.0), time * glm.radians(40.0), glm.vec3(0.5, 1.0, 0.0))
        # The normal matrix corrects normals when the model matrix includes
        # non-uniform scaling.  It is the transpose of the inverse of the
        # upper-left 3×3 of the model matrix.  For pure rotation (no scaling)
        # this equals the model matrix itself, but we compute it correctly
        # here to handle the general case.
        normal_matrix = glm.mat3(glm.transpose(glm.inverse(model)))

        self.object_program['model'].write(model)
        self.object_program['normal_matrix'].write(normal_matrix)
        self.object_program['u_light_pos'] = tuple(light_pos)
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

    scene.render(pygame.time.get_ticks() / 1000.0)
    pygame.display.flip()

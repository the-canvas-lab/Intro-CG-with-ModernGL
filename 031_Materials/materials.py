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

# Real-world material presets from http://devernay.free.fr/cours/opengl/materials.html
# Try swapping MATERIAL_EMERALD for any of the others.
MATERIAL_EMERALD = {
    'ambient':   (0.0215,  0.1745,   0.0215),
    'diffuse':   (0.07568, 0.61424,  0.07568),
    'specular':  (0.633,   0.727811, 0.633),
    'shininess': 76.8,
}
MATERIAL_GOLD = {
    'ambient':   (0.24725,  0.1995,   0.0745),
    'diffuse':   (0.75164,  0.60648,  0.22648),
    'specular':  (0.628281, 0.555802, 0.366065),
    'shininess': 51.2,
}
MATERIAL_CYAN_PLASTIC = {
    'ambient':   (0.0,  0.1,  0.06),
    'diffuse':   (0.0,  0.50980392, 0.50980392),
    'specular':  (0.50196078, 0.50196078, 0.50196078),
    'shininess': 32.0,
}

ACTIVE_MATERIAL = MATERIAL_CYAN_PLASTIC


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

        m = ACTIVE_MATERIAL
        self.object_program['material.ambient']   = m['ambient']
        self.object_program['material.diffuse']   = m['diffuse']
        self.object_program['material.specular']  = m['specular']
        self.object_program['material.shininess'] = m['shininess']

        # Attenuated light intensities — using (1,1,1) for all three makes
        # the object appear unrealistically bright because the material's
        # ambient component is already assumed to account for a dim scene.
        self.object_program['light.ambient']  = (0.2, 0.2, 0.2)
        self.object_program['light.diffuse']  = (0.5, 0.5, 0.5)
        self.object_program['light.specular'] = (1.0, 1.0, 1.0)

        self.object_program['u_view_pos'] = tuple(self.camera_pos)

    def render(self, time):
        self.ctx.clear(0.1, 0.1, 0.1)

        light_pos = glm.vec3(1.0 * math.cos(time), 2.0, 1.0 * math.sin(time))

        model = glm.rotate(glm.mat4(1.0), time * glm.radians(40.0), glm.vec3(0.5, 1.0, 0.0))
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

    scene.render(pygame.time.get_ticks() / 1000.0)
    pygame.display.flip()

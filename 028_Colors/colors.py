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


def load_obj_positions(path):
    base = os.path.dirname(os.path.abspath(__file__))
    scene = pywavefront.Wavefront(
        os.path.join(base, path),
        create_materials=True,
        parse=True,
    )
    # pywavefront flattens face data into T2F_N3F_V3F interleaved layout:
    #   [u, v, nx, ny, nz, x, y, z]  per vertex  (8 floats)
    # We only need positions here, so we discard the first 5 columns.
    all_verts = []
    for material in scene.materials.values():
        if material.vertices:
            all_verts.extend(material.vertices)
    verts = np.array(all_verts, dtype='f4').reshape(-1, 8)
    return np.ascontiguousarray(verts[:, 5:])  # columns 5,6,7 → x,y,z


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

        # Both objects share the same geometry loaded from the OBJ file.
        positions = load_obj_positions('../models/cube.obj')
        self.vbo = self.ctx.buffer(positions)

        self.object_vao = self.ctx.vertex_array(
            self.object_program, [(self.vbo, '3f', 'in_position')]
        )
        self.lamp_vao = self.ctx.vertex_array(
            self.lamp_program, [(self.vbo, '3f', 'in_position')]
        )

        # Camera above and behind the origin, looking toward it.
        camera_pos = glm.vec3(0.0, 4.0, -6.0)
        view       = glm.lookAt(camera_pos, glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))
        projection = glm.perspective(glm.radians(40.0), 800.0 / 600.0, 0.1, 100.0)

        for prog in (self.object_program, self.lamp_program):
            prog['view'].write(view)
            prog['projection'].write(projection)

        # Coral object under white light — change these to explore color reflection.
        self.object_program['u_object_color'] = (1.0, 0.5, 0.31)
        self.object_program['u_light_color']  = (1.0, 1.0, 1.0)

    def render(self, time):
        self.ctx.clear(0.1, 0.1, 0.1)

        # Lamp orbits around the y-axis at a fixed height above the cube.
        light_pos = glm.vec3(1.0 * math.cos(time), 2.0, 1.0 * math.sin(time))

        # Object sits at the origin, rotating slowly so all faces are visible.
        model = glm.rotate(glm.mat4(1.0), time * glm.radians(40.0), glm.vec3(0.5, 1.0, 0.0))
        self.object_program['model'].write(model)
        # Notice: moving the lamp has no effect on the object's shading —
        # the fragment shader only multiplies two colours, ignoring position.
        # Positional lighting is introduced in lesson 029.
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

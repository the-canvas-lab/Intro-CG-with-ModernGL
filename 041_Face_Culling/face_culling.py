# =============================================================================
# Lesson 041 — Face Culling
# =============================================================================
# Every triangle has a front face and a back face, determined by the order in
# which its vertices wind around when viewed from the camera:
#
#   Counter-clockwise (CCW) → front face   (OpenGL default)
#   Clockwise (CW)          → back face
#
# cube.obj stores its exterior faces with CW winding, so we tell OpenGL to
# treat CW as the front face:
#
#   ctx.front_face = 'cw'
#
# Without this the exterior faces would be mislabelled as back faces, culled
# in the wrong mode, and coloured blue by the shader.
#
# Modes (← →):
#
#   0 — No culling       All triangles sent to the rasteriser.
#   1 — Cull back        Back-facing (interior) triangles discarded early.
#   2 — Cull front       Front-facing (exterior) triangles discarded — the
#                        near faces disappear, exposing the blue interior.
#
# Modes 0 and 1 look identical: for a solid convex mesh the depth test already
# prevents back faces from reaching the colour buffer, so culling them is a
# pure performance win with no visual change.  The gl_FrontFacing colouring in
# the fragment shader (blue for back faces) makes mode 2 immediately obvious.
#
# Controls:  ← / → — switch mode   Esc — quit
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
        os.path.join(base, path), create_materials=True, parse=True,
    )
    all_verts = []
    for mat in scene.materials.values():
        if mat.vertices:
            all_verts.extend(mat.vertices)
    verts = np.array(all_verts, dtype='f4').reshape(-1, 8)
    return np.ascontiguousarray(np.hstack([verts[:, 5:], verts[:, 2:5], verts[:, 0:2]]))


MODES = ["No culling", "Cull back (default)", "Cull front"]


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.front_face = 'cw'  # cube.obj uses CW winding for exterior faces

        self.program = self.ctx.program(
            vertex_shader=load_shader('shaders/object.vert'),
            fragment_shader=load_shader('shaders/object.frag'),
        )

        # Only position and UV are needed — skip the normal data (12 bytes).
        vbo = self.ctx.buffer(load_obj_mesh('../models/cube.obj'))
        self.vao = self.ctx.vertex_array(
            self.program,
            [(vbo, '3f 12x 2f', 'in_position', 'in_uv')],
        )

        load_texture(self.ctx, '../images/container2.png').use(location=0)
        self.program['u_texture'] = 0

        camera_pos = glm.vec3(0.0, 1.5, 4.0)
        view       = glm.lookAt(camera_pos, glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))
        projection = glm.perspective(glm.radians(45.0), 800.0 / 600.0, 0.1, 100.0)
        self.program['view'].write(view)
        self.program['projection'].write(projection)

        self.mode = 0
        self._apply_mode()

    def _apply_mode(self):
        if self.mode == 0:
            self.ctx.disable(moderngl.CULL_FACE)
        elif self.mode == 1:
            self.ctx.enable(moderngl.CULL_FACE)
            self.ctx.cull_face = 'back'
        else:
            self.ctx.enable(moderngl.CULL_FACE)
            self.ctx.cull_face = 'front'

        label = MODES[self.mode]
        pygame.display.set_caption(
            f"041 — Face Culling  [{self.mode + 1}/{len(MODES)}] {label}  (← →)"
        )
        print(f"[{self.mode + 1}/{len(MODES)}] {label}")

    def select_mode(self, delta):
        self.mode = (self.mode + delta) % len(MODES)
        self._apply_mode()

    def render(self, time):
        self.ctx.clear(0.1, 0.1, 0.1)
        model = glm.rotate(glm.mat4(1.0), glm.radians(time * 30.0), glm.vec3(0.5, 1.0, 0.3))
        self.program['model'].write(model)
        self.vao.render()


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

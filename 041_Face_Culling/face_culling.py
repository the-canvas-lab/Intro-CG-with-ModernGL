# =============================================================================
# Lesson 041 — Face Culling
# =============================================================================
# Every triangle has a front and a back, decided by the order its vertices
# wind on screen:
#
#   Counter-clockwise (CCW) → front face   (OpenGL default)
#   Clockwise (CW)          → back face
#
# For a closed object the camera can only ever see front faces — every back
# face is hidden behind the object itself. Telling the GPU to discard them
# early ("cull" them) skips rasterising roughly half of all triangles for
# free, which is why every real game has back-face culling enabled.
#
# To make each mode VISIBLE, this box is missing its front wall, so the
# camera can see inside as it spins. The fragment shader detects back faces
# with gl_FrontFacing and colours each interior wall a slightly different
# blue (via a per-face ID vertex attribute) — the inside reads as a room
# with five distinguishable walls.
#
# Modes (← →):
#
#   1 — No culling     Through the opening you see the blue interior walls.
#
#   2 — Cull back      The blue interior is GONE: when the opening points at
#                      you, you look straight through to the background.
#                      This is the classic "see-through walls" artifact when
#                      a game camera clips inside geometry — the walls are
#                      still there, you are just seeing their culled side.
#
#   3 — Cull front     The exact opposite: the textured exterior vanishes
#                      and only the blue interior is drawn — the box appears
#                      turned inside out.
#
# Remember: on a CLOSED mesh, modes 1 and 2 would look identical, because
# the depth test already hides back faces — culling them merely saves the
# work. Only an open (or camera-penetrated) mesh reveals the difference.
#
# The vertices below are wound CCW as seen from OUTSIDE the box, matching
# the OpenGL default. Winding mistakes are the #1 cause of "my model has
# holes when culling is on" — flip two vertices of a triangle below and
# watch that wall vanish in mode 2.
#
# Controls:  ← / → — switch mode   Esc — quit
# =============================================================================

import os
import sys

import glm
import moderngl
import numpy as np
import pygame

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


def load_texture(ctx, path):
    base = os.path.dirname(os.path.abspath(__file__))
    image = pygame.image.load(os.path.join(base, path)).convert_alpha()
    image = pygame.transform.flip(image, False, True)
    data  = pygame.image.tostring(image, 'RGBA')
    tex   = ctx.texture(image.get_size(), 4, data)
    tex.build_mipmaps()
    return tex


# An OPEN box: 5 faces, each wound CCW when viewed from outside.
# The front face (z = +0.5) is deliberately missing — that is the opening.
#
# The last attribute is a per-face ID (0–4). The fragment shader uses it to
# give each INTERIOR wall a slightly different tint, so the inside reads as
# a room with distinguishable walls instead of one flat colour.
# Layout: pos(3f) uv(2f) face_id(1f)
BOX_VERTS = np.array([
    # back face (z = -0.5)                    id
    -0.5, -0.5, -0.5,  0.0, 0.0,  0,
     0.5,  0.5, -0.5,  1.0, 1.0,  0,
     0.5, -0.5, -0.5,  1.0, 0.0,  0,
     0.5,  0.5, -0.5,  1.0, 1.0,  0,
    -0.5, -0.5, -0.5,  0.0, 0.0,  0,
    -0.5,  0.5, -0.5,  0.0, 1.0,  0,
    # left face (x = -0.5)
    -0.5,  0.5,  0.5,  1.0, 0.0,  1,
    -0.5,  0.5, -0.5,  1.0, 1.0,  1,
    -0.5, -0.5, -0.5,  0.0, 1.0,  1,
    -0.5, -0.5, -0.5,  0.0, 1.0,  1,
    -0.5, -0.5,  0.5,  0.0, 0.0,  1,
    -0.5,  0.5,  0.5,  1.0, 0.0,  1,
    # right face (x = +0.5)
     0.5,  0.5,  0.5,  1.0, 0.0,  2,
     0.5, -0.5, -0.5,  0.0, 1.0,  2,
     0.5,  0.5, -0.5,  1.0, 1.0,  2,
     0.5, -0.5, -0.5,  0.0, 1.0,  2,
     0.5,  0.5,  0.5,  1.0, 0.0,  2,
     0.5, -0.5,  0.5,  0.0, 0.0,  2,
    # bottom face (y = -0.5)
    -0.5, -0.5, -0.5,  0.0, 1.0,  3,
     0.5, -0.5, -0.5,  1.0, 1.0,  3,
     0.5, -0.5,  0.5,  1.0, 0.0,  3,
     0.5, -0.5,  0.5,  1.0, 0.0,  3,
    -0.5, -0.5,  0.5,  0.0, 0.0,  3,
    -0.5, -0.5, -0.5,  0.0, 1.0,  3,
    # top face (y = +0.5)
    -0.5,  0.5, -0.5,  0.0, 1.0,  4,
     0.5,  0.5,  0.5,  1.0, 0.0,  4,
     0.5,  0.5, -0.5,  1.0, 1.0,  4,
     0.5,  0.5,  0.5,  1.0, 0.0,  4,
    -0.5,  0.5, -0.5,  0.0, 1.0,  4,
    -0.5,  0.5,  0.5,  0.0, 0.0,  4,
], dtype='f4')


MODES = ["No culling — blue interior visible",
         "Cull back — see straight through the opening",
         "Cull front — inside out"]


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)
        # CCW = front is already the default; stated explicitly because the
        # winding convention is the entire subject of this lesson.
        self.ctx.front_face = 'ccw'

        self.program = self.ctx.program(
            vertex_shader=load_shader('shaders/object.vert'),
            fragment_shader=load_shader('shaders/object.frag'),
        )

        vbo = self.ctx.buffer(BOX_VERTS)
        self.vao = self.ctx.vertex_array(
            self.program,
            [(vbo, '3f 2f 1f', 'in_position', 'in_uv', 'in_face_id')],
        )

        load_texture(self.ctx, '../images/container2.png').use(location=0)
        self.program['u_texture'] = 0

        camera_pos = glm.vec3(0.0, 0.9, 2.6)
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
        # Spin about Y so the opening sweeps past the camera once per turn.
        model = glm.rotate(glm.mat4(1.0), glm.radians(time * 40.0), glm.vec3(0.0, 1.0, 0.0))
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

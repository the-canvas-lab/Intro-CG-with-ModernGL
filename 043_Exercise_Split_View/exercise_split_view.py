# =============================================================================
# Exercise 043 — Split-View Post-Processing
# =============================================================================
# The window is 1600×600.  The scene is rendered once into an 800×600 FBO.
# Pass 2 draws two side-by-side half-screen quads that both sample that FBO
# texture:
#
#   Left  half  — passthrough (the original scene, already implemented)
#   Right half  — your post-processing effect
#
# There are three TODOs:
#
#   TODO 1  (here)         — create the offscreen FBO.
#   TODO 2  (here)         — build the two screen-quad programs and VAOs.
#   TODO 3  (effect.frag)  — implement the grayscale effect.
#
# Controls:  Esc — quit
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
pygame.display.set_mode((1600, 600), flags=pygame.OPENGL | pygame.DOUBLEBUF, vsync=True)

W, H = 800, 600   # FBO / half-window dimensions


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


# Each half-screen quad: NDC x covers its half, UV x covers the full 0→1 range
# so both sides show the complete 800×600 scene.
#
#   Left  quad:  NDC x  -1 → 0
#   Right quad:  NDC x   0 → 1
#
# Vertex layout: (ndc_x, ndc_y, uv_x, uv_y)
LEFT_QUAD = np.array([
    -1.0,  1.0,  0.0, 1.0,
    -1.0, -1.0,  0.0, 0.0,
     0.0, -1.0,  1.0, 0.0,
    -1.0,  1.0,  0.0, 1.0,
     0.0, -1.0,  1.0, 0.0,
     0.0,  1.0,  1.0, 1.0,
], dtype='f4')

RIGHT_QUAD = np.array([
     0.0,  1.0,  0.0, 1.0,
     0.0, -1.0,  0.0, 0.0,
     1.0, -1.0,  1.0, 0.0,
     0.0,  1.0,  0.0, 1.0,
     1.0, -1.0,  1.0, 0.0,
     1.0,  1.0,  1.0, 1.0,
], dtype='f4')

CUBE_POSITIONS = [
    glm.vec3( 0.0,  0.0,  0.0),
    glm.vec3( 2.0,  5.0, -15.0),
    glm.vec3(-1.5, -2.2, -2.5),
    glm.vec3(-3.8, -2.0, -12.3),
    glm.vec3( 2.4, -0.4, -3.5),
    glm.vec3(-1.7,  3.0, -7.5),
    glm.vec3( 1.3, -2.0, -2.5),
    glm.vec3( 1.5,  2.0, -2.5),
    glm.vec3( 1.5,  0.2, -1.5),
    glm.vec3(-1.3,  1.0, -1.5),
]


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()

        # --- scene shader (Pass 1) ---
        self.scene_prog = self.ctx.program(
            vertex_shader=load_shader('shaders/scene.vert'),
            fragment_shader=load_shader('shaders/scene.frag'),
        )

        vbo = self.ctx.buffer(load_obj_mesh('../models/cube.obj'))
        self.scene_vao = self.ctx.vertex_array(
            self.scene_prog,
            [(vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_uv')],
        )

        load_texture(self.ctx, '../images/container2.png').use(location=0)
        self.scene_prog['u_texture'] = 0

        view       = glm.lookAt(glm.vec3(0.0, 0.0, 5.0), glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))
        projection = glm.perspective(glm.radians(45.0), W / H, 0.1, 100.0)
        self.scene_prog['view'].write(view)
        self.scene_prog['projection'].write(projection)

        # TODO 1 — Create the offscreen FBO.
        #
        # You need three objects:
        #   self.color_tex  — a moderngl texture, size (W, H), 4 channels (RGBA).
        #                     Set its filter to (moderngl.LINEAR, moderngl.LINEAR).
        #   depth_buf       — a depth renderbuffer, same size.  The depth test
        #                     requires it even though we never sample it.
        #   self.fbo        — a framebuffer that attaches both:
        #                       color_attachments=[self.color_tex]
        #                       depth_attachment=depth_buf
        #
        # Finally bind self.color_tex to texture unit 1 so it doesn't clash
        # with the scene texture already on unit 0.

        # TODO 2 — Build the two screen-quad programs and VAOs.
        #
        # Left half  — passthrough:
        #   self.passthrough_prog: screen.vert + passthrough.frag
        #   Tell it u_screen = 1  (the FBO texture unit).
        #   self.left_vao: vertex array using LEFT_QUAD buffer, format '2f 2f',
        #                  attributes 'in_position' and 'in_uv'.
        #
        # Right half  — your effect:
        #   self.effect_prog: screen.vert + effect.frag
        #   Tell it u_screen = 1.
        #   self.right_vao: same setup using RIGHT_QUAD buffer.

        pygame.display.set_caption("043 — Split-View  |  left: original   right: your effect")

    def render(self, time):
        # ------------------------------------------------------------------
        # Pass 1 — render the 10-cube scene into the offscreen FBO.
        # ------------------------------------------------------------------
        self.fbo.use()
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.clear(0.1, 0.1, 0.1)

        for i, pos in enumerate(CUBE_POSITIONS):
            angle = glm.radians(20.0 * i + time * 30.0)
            model = glm.translate(glm.mat4(1.0), pos)
            model = glm.rotate(model, angle, glm.vec3(1.0, 0.3, 0.5))
            self.scene_prog['model'].write(model)
            self.scene_prog['normal_matrix'].write(
                glm.mat3(glm.transpose(glm.inverse(model)))
            )
            self.scene_vao.render()

        # ------------------------------------------------------------------
        # Pass 2 — draw both half-screen quads onto the window.
        # ------------------------------------------------------------------
        self.ctx.screen.use()
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.clear(0.0, 0.0, 0.0)

        self.color_tex.use(location=1)
        self.left_vao.render()   # left  — passthrough
        self.right_vao.render()  # right — your effect


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

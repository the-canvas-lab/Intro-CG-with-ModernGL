# =============================================================================
# Lesson 042 — Framebuffers
# =============================================================================
# Normally every draw call writes directly to the default framebuffer (the
# window).  A Framebuffer Object (FBO) gives you an offscreen render target
# instead — a colour texture (and optional depth buffer) that the GPU writes
# to, just like it would write to the screen.
#
# Two-pass pipeline used here:
#
#   Pass 1  — render the 10-cube scene into an FBO colour texture.
#   Pass 2  — draw a full-screen quad, sampling that texture and applying a
#              screen-space post-processing effect.
#
# Because Pass 2 reads from a regular texture it can do anything a fragment
# shader can do: inversion, grayscale, convolution kernels, etc.
#
# FBO setup (one time):
#
#   color_tex = ctx.texture((W, H), 4)          # RGBA render target
#   depth_buf = ctx.depth_renderbuffer((W, H))   # depth storage (write-only)
#   fbo       = ctx.framebuffer(color_attachments=[color_tex],
#                                depth_attachment=depth_buf)
#
# Each frame:
#
#   fbo.use()            # redirect all draws to the FBO
#   draw scene ...
#   ctx.screen.use()     # redirect back to the window
#   draw screen quad ... # sample color_tex and apply effect
#
# Post-processing modes (← →):
#
#   0 — None            Passthrough — the scene rendered normally.
#   1 — Inversion       Flip each colour channel (1 − c).
#   2 — Grayscale       Luminance-weighted conversion to grey.
#   3 — Sharpen         3×3 convolution: enhances edges/detail.
#   4 — Blur            3×3 box filter: averages surrounding pixels.
#   5 — Edge detection  Laplacian kernel: highlights contours on black.
#
# Controls:  ← / → — switch effect   Esc — quit
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

W, H = 800, 600


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
    # reorder T2F_N3F_V3F → [pos(3), nrm(3), uv(2)]
    return np.ascontiguousarray(np.hstack([verts[:, 5:], verts[:, 2:5], verts[:, 0:2]]))


# Full-screen NDC quad: two triangles covering the entire clip-space rectangle.
# Position (xy) ranges from -1 to +1; UV (st) ranges from 0 to 1.
SCREEN_QUAD = np.array([
    -1.0,  1.0,  0.0, 1.0,
    -1.0, -1.0,  0.0, 0.0,
     1.0, -1.0,  1.0, 0.0,
    -1.0,  1.0,  0.0, 1.0,
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

MODES = [
    "None",
    "Inversion",
    "Grayscale",
    "Sharpen",
    "Blur",
    "Edge Detection",
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

        camera_pos = glm.vec3(0.0, 0.0, 5.0)
        view       = glm.lookAt(camera_pos, glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))
        projection = glm.perspective(glm.radians(45.0), W / H, 0.1, 100.0)
        self.scene_prog['view'].write(view)
        self.scene_prog['projection'].write(projection)

        # --- offscreen FBO ---
        self.color_tex = self.ctx.texture((W, H), 4)
        self.color_tex.filter = moderngl.LINEAR, moderngl.LINEAR
        depth_buf  = self.ctx.depth_renderbuffer((W, H))
        self.fbo   = self.ctx.framebuffer(
            color_attachments=[self.color_tex],
            depth_attachment=depth_buf,
        )

        # --- screen quad shader (Pass 2) ---
        self.screen_prog = self.ctx.program(
            vertex_shader=load_shader('shaders/screen.vert'),
            fragment_shader=load_shader('shaders/screen.frag'),
        )
        quad_vbo = self.ctx.buffer(SCREEN_QUAD.tobytes())
        self.screen_vao = self.ctx.vertex_array(
            self.screen_prog,
            [(quad_vbo, '2f 2f', 'in_position', 'in_uv')],
        )

        # FBO colour texture goes to unit 1 so it doesn't clash with the scene
        # texture on unit 0.
        self.color_tex.use(location=1)
        self.screen_prog['u_screen'] = 1

        self.mode = 0
        self._apply_mode()

    def _apply_mode(self):
        self.screen_prog['u_mode'] = self.mode
        label = MODES[self.mode]
        pygame.display.set_caption(
            f"042 — Framebuffers  [{self.mode + 1}/{len(MODES)}] {label}  (← →)"
        )
        print(f"[{self.mode + 1}/{len(MODES)}] {label}")

    def select_mode(self, delta):
        self.mode = (self.mode + delta) % len(MODES)
        self._apply_mode()

    def render(self, time):
        # ------------------------------------------------------------------
        # Pass 1 — render 10-cube scene into the offscreen FBO.
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
        # Pass 2 — draw full-screen quad with the post-processing effect.
        # ------------------------------------------------------------------
        self.ctx.screen.use()
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.ctx.clear(1.0, 1.0, 1.0)

        self.color_tex.use(location=1)
        self.screen_vao.render()


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

# =============================================================================
# Lesson 051 — Shadow Mapping
# =============================================================================
# Rasterization has no concept of "is something between me and the light?" —
# each triangle is shaded in isolation. Shadow mapping answers the question
# with a clever reuse of the depth buffer (038) and framebuffers (042):
#
#   PASS 1  render the scene FROM THE LIGHT's point of view into a
#           depth-only FBO. The resulting "shadow map" stores, per direction,
#           the distance to the nearest surface the light can see.
#
#   PASS 2  render normally from the camera. Project each fragment into the
#           light's clip space (one extra matrix multiply) and compare its
#           depth against the shadow map: if the light recorded something
#           NEARER, this fragment is occluded -> in shadow.
#
# Two classic artifacts are toggleable so you can meet them on purpose:
#
#   B — depth BIAS off/on. Without it, surfaces shadow THEMSELVES in moiré
#       stripes ("shadow acne") because the map's finite resolution makes
#       the depth comparison zig-zag around equality.
#   P — PCF off/on. A single depth comparison gives hard, blocky shadow
#       edges; percentage-closer filtering averages 9 comparisons for a
#       softer edge.
#
# The small overlay (bottom-right) shows the raw shadow map — pass 1's view
# of the world, straight from the light.
#
# Controls:  WASD — move   Mouse — look   B — bias   P — PCF
#            Space — pause the orbiting light   Esc — quit
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


SHADOW_SIZE = 1024

# Floor: pos(3f) normal(3f) uv(2f), tiled 8x8.
S, UV = 12.0, 8.0
FLOOR_VERTS = np.array([
    -S, 0, -S,  0, 1, 0,   0,  0,
     S, 0, -S,  0, 1, 0,  UV,  0,
     S, 0,  S,  0, 1, 0,  UV, UV,
    -S, 0, -S,  0, 1, 0,   0,  0,
     S, 0,  S,  0, 1, 0,  UV, UV,
    -S, 0,  S,  0, 1, 0,   0, UV,
], dtype='f4')

DEBUG_QUAD_VERTS = np.array([
    -0.5, -0.5,  0.0, 0.0,
     0.5, -0.5,  1.0, 0.0,
     0.5,  0.5,  1.0, 1.0,
    -0.5, -0.5,  0.0, 0.0,
     0.5,  0.5,  1.0, 1.0,
    -0.5,  0.5,  0.0, 1.0,
], dtype='f4')


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)

        self.depth_program = self.ctx.program(
            vertex_shader=load_shader('shaders/depth.vert'),
            fragment_shader=load_shader('shaders/depth.frag'),
        )
        self.scene_program = self.ctx.program(
            vertex_shader=load_shader('shaders/scene.vert'),
            fragment_shader=load_shader('shaders/scene.frag'),
        )
        self.debug_program = self.ctx.program(
            vertex_shader=load_shader('shaders/debug.vert'),
            fragment_shader=load_shader('shaders/debug.frag'),
        )

        # --- pass-1 target: a depth-only framebuffer -----------------------
        self.shadow_map = self.ctx.depth_texture((SHADOW_SIZE, SHADOW_SIZE))
        # By default a depth texture samples as a comparison ("shadow")
        # sampler; disable that so the shader reads raw depth values.
        self.shadow_map.compare_func = ''
        self.shadow_map.filter   = (moderngl.NEAREST, moderngl.NEAREST)
        self.shadow_map.repeat_x = False
        self.shadow_map.repeat_y = False
        self.shadow_fbo = self.ctx.framebuffer(depth_attachment=self.shadow_map)

        # --- geometry: each mesh gets a VAO per program ---------------------
        floor_vbo = self.ctx.buffer(FLOOR_VERTS)
        cube_vbo  = self.ctx.buffer(load_obj_mesh('../models/cube.obj'))
        full_fmt  = ('3f 3f 2f', 'in_position', 'in_normal', 'in_uv')
        depth_fmt = ('3f 5x4', 'in_position')   # pass 1 needs positions only
        self.floor_scene = self.ctx.vertex_array(self.scene_program, [(floor_vbo, *full_fmt)])
        self.floor_depth = self.ctx.vertex_array(self.depth_program, [(floor_vbo, *depth_fmt)])
        self.cube_scene  = self.ctx.vertex_array(self.scene_program, [(cube_vbo, *full_fmt)])
        self.cube_depth  = self.ctx.vertex_array(self.depth_program, [(cube_vbo, *depth_fmt)])

        debug_vbo = self.ctx.buffer(DEBUG_QUAD_VERTS)
        self.debug_vao = self.ctx.vertex_array(
            self.debug_program, [(debug_vbo, '2f 2f', 'in_position', 'in_uv')])

        self.floor_texture = load_texture(self.ctx, '../images/wall.jpg')
        self.cube_texture  = load_texture(self.ctx, '../images/container2.png')
        self.scene_program['u_texture']    = 0
        self.scene_program['u_shadow_map'] = 1
        self.debug_program['u_depth']      = 1

        projection = glm.perspective(glm.radians(45.0), 800.0 / 600.0, 0.1, 100.0)
        self.scene_program['projection'].write(projection)

        # Cubes: (translate, rotate_angle, rotate_axis, scale)
        self.cube_params = [
            (glm.vec3(-2.2, 0.5, -1.0), 0.0,  glm.vec3(0, 1, 0), 1.0),
            (glm.vec3(1.8, 0.5, 1.4),   0.6,  glm.vec3(0, 1, 0), 1.0),
            (glm.vec3(0.0, 1.9, 0.2),   0.9,  glm.vec3(1, 0, 1), 0.6),
        ]

        # Camera (free-fly, lesson 025)
        self.camera_pos  = glm.vec3(6.0, 4.5, 9.0)
        self.yaw         = -120.0
        self.pitch       = -18.0
        self.speed       = 5.0
        self.sensitivity = 0.1
        self.camera_front = glm.vec3(0.0, 0.0, -1.0)
        self.camera_up    = glm.vec3(0.0, 1.0, 0.0)
        self.update_front()

        self.use_bias  = True
        self.use_pcf   = True
        self.paused    = False
        self.light_angle = 0.6
        self.update_caption()

        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

    def update_caption(self):
        pygame.display.set_caption(
            "051 — Shadow Mapping   "
            f"[B]ias: {'on' if self.use_bias else 'OFF -> acne!'}   "
            f"[P]CF: {'on' if self.use_pcf else 'off'}   [Space] light")

    def update_front(self):
        front = glm.vec3(
            math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch)),
            math.sin(glm.radians(self.pitch)),
            math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch)),
        )
        self.camera_front = glm.normalize(front)

    def handle_mouse(self, dx, dy):
        self.yaw   += dx * self.sensitivity
        self.pitch -= dy * self.sensitivity
        self.pitch  = max(-89.0, min(89.0, self.pitch))
        self.update_front()

    def toggle(self, key):
        if key == pygame.K_b:
            self.use_bias = not self.use_bias
        elif key == pygame.K_p:
            self.use_pcf = not self.use_pcf
        elif key == pygame.K_SPACE:
            self.paused = not self.paused
        self.update_caption()

    def cube_models(self):
        for pos, angle, axis, scale in self.cube_params:
            model = glm.translate(glm.mat4(1.0), pos)
            model = glm.rotate(model, angle, axis)
            model = glm.scale(model, glm.vec3(scale))
            yield model

    def render(self, dt):
        # --- camera movement -------------------------------------------------
        keys  = pygame.key.get_pressed()
        right = glm.normalize(glm.cross(self.camera_front, self.camera_up))
        v = self.speed * dt
        if keys[pygame.K_w]: self.camera_pos += self.camera_front * v
        if keys[pygame.K_s]: self.camera_pos -= self.camera_front * v
        if keys[pygame.K_a]: self.camera_pos -= right * v
        if keys[pygame.K_d]: self.camera_pos += right * v

        # --- light: slow orbit, directional, orthographic --------------------
        if not self.paused:
            self.light_angle += dt * 0.3
        light_pos = glm.vec3(math.cos(self.light_angle) * 8.0, 7.0,
                             math.sin(self.light_angle) * 8.0)
        # A directional light has no real position: the orthographic box just
        # needs to contain everything that can cast a visible shadow.
        light_space = (glm.ortho(-14.0, 14.0, -14.0, 14.0, 1.0, 40.0)
                       * glm.lookAt(light_pos, glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0)))

        # ===== PASS 1: depth from the light into the shadow FBO ==============
        self.shadow_fbo.use()           # also sets the viewport to 1024x1024
        self.shadow_fbo.clear()
        self.depth_program['u_light_space'].write(light_space)

        self.depth_program['model'].write(glm.mat4(1.0))
        self.floor_depth.render()
        for model in self.cube_models():
            self.depth_program['model'].write(model)
            self.cube_depth.render()

        # ===== PASS 2: normal render, sampling the shadow map ================
        self.ctx.screen.use()
        self.ctx.clear(0.08, 0.09, 0.12)

        view = glm.lookAt(self.camera_pos,
                          self.camera_pos + self.camera_front, self.camera_up)
        self.scene_program['view'].write(view)
        self.scene_program['u_light_space'].write(light_space)
        self.scene_program['u_light_dir'] = tuple(glm.normalize(light_pos))
        self.scene_program['u_use_bias'] = self.use_bias
        self.scene_program['u_use_pcf']  = self.use_pcf
        self.shadow_map.use(location=1)

        self.floor_texture.use(location=0)
        self.scene_program['model'].write(glm.mat4(1.0))
        self.scene_program['normal_matrix'].write(glm.mat3(1.0))
        self.floor_scene.render()

        self.cube_texture.use(location=0)
        for model in self.cube_models():
            self.scene_program['model'].write(model)
            self.scene_program['normal_matrix'].write(
                glm.mat3(glm.transpose(glm.inverse(model))))
            self.cube_scene.render()

        # --- overlay: the raw shadow map, as in lesson 042's mini quad -------
        self.ctx.disable(moderngl.DEPTH_TEST)
        self.debug_program['u_pos']   = (0.72, -0.62)
        self.debug_program['u_scale'] = (0.5, 0.5 * 800.0 / 600.0)
        self.debug_vao.render()
        self.ctx.enable(moderngl.DEPTH_TEST)


scene = Scene()
clock = pygame.time.Clock()

while True:
    dt = min(clock.tick(60) / 1000.0, 0.05)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key in (pygame.K_b, pygame.K_p, pygame.K_SPACE):
                scene.toggle(event.key)
        if event.type == pygame.MOUSEMOTION:
            scene.handle_mouse(*event.rel)

    scene.render(dt)
    pygame.display.flip()

# =============================================================================
# Lesson 046 — Asteroid Field (no instancing)
# =============================================================================
# Baseline before Lesson 047: AMOUNT asteroids drawn with one draw call each.
#
# The render loop updates a uniform mat4 model and calls vao.render() once per
# rock — AMOUNT + 1 draw calls total (planet + belt):
#
#   for m in self.matrices:
#       self.prog['model'].write(m)
#       self.asteroid_vao.render()
#
# Both the planet and asteroids share a single shader program (object.vert /
# object.frag) since they both need only a uniform model matrix.
#
# At AMOUNT = 1,000 the CPU overhead is noticeable; at higher counts (10k,
# 100k) the scene becomes unrunnable.  Lesson 047 fixes this in 1 draw call.
#
# Asteroid placement matches learnopengl.com 10.2 / 10.3:
#   - Angles are evenly distributed around 360°.
#   - Each position is scattered by a random ±25 unit displacement.
#   - The belt is flattened: y displacement is scaled by 0.4.
#   - Random scale 0.05–0.24; rotation around axis (0.4, 0.6, 0.8).
#
# Controls:  W A S D — move   Mouse — look   Scroll — zoom   Esc — quit
# =============================================================================

import math
import os
import random
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
pygame.display.set_caption("046 — Asteroid Field  (no instancing — 1,001 draw calls)")

AMOUNT       = 500_000
RING_RADIUS  = 150.0
RING_OFFSET  = 25.0
CAMERA_SPEED = 20.0
MOUSE_SENS   = 0.1


def load_shader(path):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path), encoding='utf-8') as f:
        return f.read()


def load_texture(ctx, path):
    base  = os.path.dirname(os.path.abspath(__file__))
    image = pygame.image.load(os.path.join(base, path)).convert_alpha()
    image = pygame.transform.flip(image, False, True)
    data  = pygame.image.tostring(image, 'RGBA')
    tex   = ctx.texture(image.get_size(), 4, data)
    tex.build_mipmaps()
    return tex


def load_obj_mesh(path):
    base  = os.path.dirname(os.path.abspath(__file__))
    scene = pywavefront.Wavefront(
        os.path.join(base, path), create_materials=True, parse=True,
    )
    all_verts = []
    for mat in scene.materials.values():
        if mat.vertices:
            all_verts.extend(mat.vertices)
    verts = np.array(all_verts, dtype='f4').reshape(-1, 8)
    # Reorder T2F_N3F_V3F → [pos(3), nrm(3), uv(2)]
    return np.ascontiguousarray(np.hstack([verts[:, 5:], verts[:, 2:5], verts[:, 0:2]]))


def build_asteroid_matrices():
    """AMOUNT model matrices arranged in an asteroid belt.

    Identical placement to Lesson 047 (learnopengl.com 10.3).
    Returns a list of glm.mat4; each is written as a uniform per draw call.
    """
    max_disp = int(2 * RING_OFFSET * 100)  # 5000  →  scatter range -25..+24.99
    out = []
    for i in range(AMOUNT):
        m = glm.mat4(1.0)

        angle = i / AMOUNT * 360.0

        displacement = random.randint(0, max_disp - 1) / 100.0 - RING_OFFSET
        x = math.sin(math.radians(angle)) * RING_RADIUS + displacement

        displacement = random.randint(0, max_disp - 1) / 100.0 - RING_OFFSET
        y = displacement * 0.4  # flatten the belt

        displacement = random.randint(0, max_disp - 1) / 100.0 - RING_OFFSET
        z = math.cos(math.radians(angle)) * RING_RADIUS + displacement

        m = glm.translate(m, glm.vec3(x, y, z))

        scale = random.randint(0, 19) / 100.0 + 0.05
        m = glm.scale(m, glm.vec3(scale))

        rot = float(random.randint(0, 359))
        m = glm.rotate(m, rot, glm.vec3(0.4, 0.6, 0.8))

        out.append(m)

    return out


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)

        # Single program for both planet and asteroids — both use uniform mat4 model
        self.prog = self.ctx.program(
            vertex_shader=load_shader('shaders/object.vert'),
            fragment_shader=load_shader('shaders/object.frag'),
        )
        self.prog['u_texture'] = 0

        # Planet VAO
        planet_vbo      = self.ctx.buffer(load_obj_mesh('../models/planet/planet.obj'))
        self.planet_tex = load_texture(self.ctx, '../models/planet/mars.png')
        self.planet_vao = self.ctx.vertex_array(
            self.prog,
            [(planet_vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_uv')],
        )
        self.planet_matrix = glm.scale(
            glm.translate(glm.mat4(1.0), glm.vec3(0.0, -3.0, 0.0)),
            glm.vec3(4.0),
        )

        # Asteroid VAO — no instance buffer; model is set as a uniform each frame
        rock_vbo      = self.ctx.buffer(load_obj_mesh('../models/rock/rock.obj'))
        self.rock_tex = load_texture(self.ctx, '../models/rock/rock.png')
        self.asteroid_vao = self.ctx.vertex_array(
            self.prog,
            [(rock_vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_uv')],
        )

        print(f"Building {AMOUNT:,} asteroid matrices …", end=' ', flush=True)
        self.matrices = build_asteroid_matrices()
        print("done.")

        projection = glm.perspective(glm.radians(45.0), 800.0 / 600.0, 0.1, 1000.0)
        self.prog['projection'].write(projection)

        self.camera_pos   = glm.vec3(0.0, 0.0, 120.0)
        self.camera_front = glm.vec3(0.0, 0.0, -1.0)
        self.camera_up    = glm.vec3(0.0, 1.0,  0.0)
        self.yaw   = -90.0
        self.pitch =   0.0
        self.fov   =  45.0

    def handle_scroll(self, dy):
        self.fov = max(1.0, min(45.0, self.fov - dy))
        proj = glm.perspective(glm.radians(self.fov), 800.0 / 600.0, 0.1, 1000.0)
        self.prog['projection'].write(proj)

    def render(self, delta_time):
        speed = CAMERA_SPEED * delta_time
        right = glm.normalize(glm.cross(self.camera_front, self.camera_up))
        keys  = pygame.key.get_pressed()
        if keys[pygame.K_w]: self.camera_pos += speed * self.camera_front
        if keys[pygame.K_s]: self.camera_pos -= speed * self.camera_front
        if keys[pygame.K_a]: self.camera_pos -= speed * right
        if keys[pygame.K_d]: self.camera_pos += speed * right

        dx, dy = pygame.mouse.get_rel()
        self.yaw   += dx * MOUSE_SENS
        self.pitch  = max(-89.0, min(89.0, self.pitch - dy * MOUSE_SENS))
        yr = glm.radians(self.yaw)
        pr = glm.radians(self.pitch)
        self.camera_front = glm.normalize(glm.vec3(
            math.cos(yr) * math.cos(pr),
            math.sin(pr),
            math.sin(yr) * math.cos(pr),
        ))

        view = glm.lookAt(self.camera_pos, self.camera_pos + self.camera_front, self.camera_up)
        self.prog['view'].write(view)

        self.ctx.clear(0.1, 0.1, 0.1)

        # Planet — 1 draw call
        self.planet_tex.use(location=0)
        self.prog['model'].write(self.planet_matrix)
        self.planet_vao.render()

        # Asteroid belt — AMOUNT draw calls (one uniform update + render per rock)
        self.rock_tex.use(location=0)
        for m in self.matrices:
            self.prog['model'].write(m)
            self.asteroid_vao.render()


scene = Scene()

pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
pygame.mouse.get_rel()  # discard initial delta

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEWHEEL:
            scene.handle_scroll(event.y)

    delta_time = min(clock.tick() / 1000.0, 0.1)
    scene.render(delta_time)
    pygame.display.flip()

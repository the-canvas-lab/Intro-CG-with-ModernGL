# =============================================================================
# Lesson 047 — Asteroid Field (instanced)
# =============================================================================
# Demonstrates instancing at scale: 100,000 rock models orbiting a planet,
# drawn in a single draw call.
#
# Per-instance data is a full 4×4 model matrix.  A mat4 occupies four
# consecutive attribute locations; we split it into four vec4 columns and
# upload each as its own per-instance attribute with the /i divisor:
#
#   (inst_vbo, '4f 4f 4f 4f /i', 'in_model_c0', 'in_model_c1',
#                                 'in_model_c2', 'in_model_c3')
#
# Reconstructed in the vertex shader:
#
#   mat4 model = mat4(in_model_c0, in_model_c1, in_model_c2, in_model_c3);
#
# All 100,000 matrices are computed once at startup and uploaded to a single
# VBO; the entire asteroid belt is then drawn with one call:
#
#   asteroid_vao.render(instances=AMOUNT)
#
# The planet uses a separate shader program with a plain uniform mat4 model
# (no instancing needed — it is drawn once).
#
# Asteroid placement matches the learnopengl.com 10.3 reference:
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
pygame.display.set_caption("047 — Asteroid Field  (100,000 instances, 2 draw calls)")

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

    Matches learnopengl.com 10.3: angles evenly distributed, random scatter
    displacement in [-offset, offset], y flattened by 0.4, scale 0.05–0.24,
    rotation around the fixed axis (0.4, 0.6, 0.8).
    """
    max_disp = int(2 * RING_OFFSET * 100)  # 5000  →  scatter range -25..+24.99
    out = []
    for i in range(AMOUNT):
        m = glm.mat4(1.0)

        # Evenly spaced angle so rocks form a continuous ring
        angle = i / AMOUNT * 360.0

        displacement = random.randint(0, max_disp - 1) / 100.0 - RING_OFFSET
        x = math.sin(math.radians(angle)) * RING_RADIUS + displacement

        displacement = random.randint(0, max_disp - 1) / 100.0 - RING_OFFSET
        y = displacement * 0.4  # flatten the belt

        displacement = random.randint(0, max_disp - 1) / 100.0 - RING_OFFSET
        z = math.cos(math.radians(angle)) * RING_RADIUS + displacement

        m = glm.translate(m, glm.vec3(x, y, z))

        # scale 0.05 to 0.24
        scale = random.randint(0, 19) / 100.0 + 0.05
        m = glm.scale(m, glm.vec3(scale))

        # rotation: integer degrees passed directly as radians to match the
        # reference (produces valid random orientations regardless of units)
        rot = float(random.randint(0, 359))
        m = glm.rotate(m, rot, glm.vec3(0.4, 0.6, 0.8))

        out.append(bytes(glm.transpose(m)))

    return b''.join(out)


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)

        # Two separate programs: planet uses a uniform model matrix;
        # asteroid uses per-instance mat4 columns.
        self.planet_prog = self.ctx.program(
            vertex_shader=load_shader('shaders/planet.vert'),
            fragment_shader=load_shader('shaders/object.frag'),
        )
        self.planet_prog['u_texture'] = 0

        self.asteroid_prog = self.ctx.program(
            vertex_shader=load_shader('shaders/asteroid.vert'),
            fragment_shader=load_shader('shaders/object.frag'),
        )
        self.asteroid_prog['u_texture'] = 0

        # Planet VAO — single uniform model matrix
        planet_vbo      = self.ctx.buffer(load_obj_mesh('../models/planet/planet.obj'))
        self.planet_tex = load_texture(self.ctx, '../models/planet/mars.png')
        self.planet_vao = self.ctx.vertex_array(
            self.planet_prog,
            [(planet_vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_uv')],
        )
        planet_m = glm.scale(
            glm.translate(glm.mat4(1.0), glm.vec3(0.0, -3.0, 0.0)),
            glm.vec3(4.0),
        )
        self.planet_prog['model'].write(planet_m)

        # Asteroid VAO — per-instance mat4 split into 4 × vec4
        rock_vbo      = self.ctx.buffer(load_obj_mesh('../models/rock/rock.obj'))
        self.rock_tex = load_texture(self.ctx, '../models/rock/rock.png')

        print(f"Building {AMOUNT:,} asteroid matrices …", end=' ', flush=True)
        inst_vbo = self.ctx.buffer(build_asteroid_matrices())
        print("done.")

        self.asteroid_vao = self.ctx.vertex_array(
            self.asteroid_prog,
            [
                (rock_vbo,  '3f 3f 2f',       'in_position', 'in_normal', 'in_uv'),
                (inst_vbo,  '4f 4f 4f 4f /i', 'in_model_c0', 'in_model_c1',
                                               'in_model_c2', 'in_model_c3'),
            ],
        )

        projection = glm.perspective(glm.radians(45.0), 800.0 / 600.0, 0.1, 1000.0)
        self.planet_prog['projection'].write(projection)
        self.asteroid_prog['projection'].write(projection)
        self._projection = projection

        # Camera: start just outside the ring, facing the planet
        self.camera_pos   = glm.vec3(0.0, 0.0, 120.0)
        self.camera_front = glm.vec3(0.0, 0.0, -1.0)
        self.camera_up    = glm.vec3(0.0, 1.0,  0.0)
        self.yaw   = -90.0
        self.pitch =   0.0
        self.fov   =  45.0

    def handle_scroll(self, dy):
        self.fov = max(1.0, min(45.0, self.fov - dy))
        proj = glm.perspective(glm.radians(self.fov), 800.0 / 600.0, 0.1, 1000.0)
        self.planet_prog['projection'].write(proj)
        self.asteroid_prog['projection'].write(proj)

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
        self.planet_prog['view'].write(view)
        self.asteroid_prog['view'].write(view)

        self.ctx.clear(0.1, 0.1, 0.1)

        # Planet — 1 draw call
        self.planet_tex.use(location=0)
        self.planet_vao.render()

        # Asteroid belt — 1 draw call, 100,000 instances
        self.rock_tex.use(location=0)
        self.asteroid_vao.render(instances=AMOUNT)


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

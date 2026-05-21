# =============================================================================
# Lesson 025 — Camera
# =============================================================================
# Adds a free-fly camera controlled by keyboard and mouse.
#
# The view matrix in lesson 023 was a static translate that placed the camera
# 3 units behind the origin.  This lesson replaces it with glm.lookAt()
# rebuilt every frame from three live camera vectors:
#
#   camera_pos    -- where the camera sits in world space
#   camera_front  -- unit vector pointing in the direction the camera looks
#   camera_up     -- world-space up direction, (0, 1, 0)
#
# Three input sub-systems update these vectors each frame:
#
#   Keyboard (WASD)
#       Moves camera_pos along camera_front (forward / back) and along the
#       right vector from cross(camera_front, camera_up) (strafe).
#       Movement is multiplied by delta_time so speed is frame-rate-independent.
#
#   Mouse look
#       Relative mouse motion updates two Euler angles: yaw (horizontal) and
#       pitch (vertical).  Trigonometric formulas reconstruct camera_front from
#       those angles each frame.  Pitch is clamped to +-89 degrees to prevent
#       a singularity when looking straight up or down.
#
#   Scroll zoom
#       Adjusts the FOV of the perspective projection.  A smaller FOV makes
#       distant objects appear larger (zoom in); a larger FOV shows more of the
#       scene (zoom out).
#
# Controls:  W A S D -- move   Mouse -- look   Scroll -- zoom   Esc -- quit
# =============================================================================

import math
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

# fmt: off
CUBE_VERTICES = np.array([
    -0.5, -0.5, -0.5,  0.0, 0.0,
     0.5, -0.5, -0.5,  1.0, 0.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
    -0.5,  0.5, -0.5,  0.0, 1.0,
    -0.5, -0.5, -0.5,  0.0, 0.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,
     0.5, -0.5,  0.5,  1.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 1.0,
     0.5,  0.5,  0.5,  1.0, 1.0,
    -0.5,  0.5,  0.5,  0.0, 1.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,
    -0.5,  0.5,  0.5,  1.0, 0.0,
    -0.5,  0.5, -0.5,  1.0, 1.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,
    -0.5,  0.5,  0.5,  1.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 0.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
     0.5, -0.5, -0.5,  0.0, 1.0,
     0.5, -0.5, -0.5,  0.0, 1.0,
     0.5, -0.5,  0.5,  0.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 0.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,
     0.5, -0.5, -0.5,  1.0, 1.0,
     0.5, -0.5,  0.5,  1.0, 0.0,
     0.5, -0.5,  0.5,  1.0, 0.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,
    -0.5,  0.5, -0.5,  0.0, 1.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
     0.5,  0.5,  0.5,  1.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 0.0,
    -0.5,  0.5,  0.5,  0.0, 0.0,
    -0.5,  0.5, -0.5,  0.0, 1.0,
], dtype='f4')

CUBE_POSITIONS = [
    glm.vec3( 0.0,  0.0,  0.0),
    glm.vec3( 2.0,  5.0, -15.0),
    glm.vec3(-1.5, -2.2,  -2.5),
    glm.vec3(-3.8, -2.0, -12.3),
    glm.vec3( 2.4, -0.4,  -3.5),
    glm.vec3(-1.7,  3.0,  -7.5),
    glm.vec3( 1.3, -2.0,  -2.5),
    glm.vec3( 1.5,  2.0,  -2.5),
    glm.vec3( 1.5,  0.2,  -1.5),
    glm.vec3(-1.3,  1.0,  -1.5),
]
# fmt: on

ROTATION_AXIS     = glm.vec3(1.0, 0.3, 0.5)
CAMERA_SPEED      = 2.5   # world units per second
MOUSE_SENSITIVITY = 0.1   # degrees per pixel


def load_shader(path):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path), encoding='utf-8') as f:
        return f.read()


def load_texture(ctx, path):
    base = os.path.dirname(os.path.abspath(__file__))
    image = pygame.image.load(os.path.join(base, path)).convert_alpha()
    image = pygame.transform.flip(image, False, True)
    data = pygame.image.tostring(image, 'RGBA')
    texture = ctx.texture(image.get_size(), 4, data)
    texture.build_mipmaps()
    return texture


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(self.ctx.DEPTH_TEST)

        self.program = self.ctx.program(
            vertex_shader=load_shader('shaders/cube.vert'),
            fragment_shader=load_shader('shaders/cube.frag'),
        )

        vbo = self.ctx.buffer(CUBE_VERTICES)
        self.vao = self.ctx.vertex_array(
            self.program,
            [(vbo, '3f 2f', 'in_position', 'in_uv')],
        )

        self.texture = load_texture(self.ctx, '../images/container.jpg')
        self.program['u_texture'] = 0

        # Camera state --------------------------------------------------------
        self.camera_pos   = glm.vec3(0.0, 0.0,  3.0)
        self.camera_front = glm.vec3(0.0, 0.0, -1.0)  # initially facing -Z
        self.camera_up    = glm.vec3(0.0, 1.0,  0.0)

        # -90 degrees aligns the initial front vector toward -Z.
        # (cos(-90)*cos(0), sin(0), sin(-90)*cos(0)) = (0, 0, -1)
        self.yaw   = -90.0
        self.pitch =   0.0
        self.fov   =  45.0

    def handle_scroll(self, delta_y):
        self.fov = max(1.0, min(45.0, self.fov - delta_y))

    def render(self, delta_time):
        # -- Keyboard: translate camera_pos each frame -----------------------
        speed = CAMERA_SPEED * delta_time
        right = glm.normalize(glm.cross(self.camera_front, self.camera_up))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: self.camera_pos += speed * self.camera_front
        if keys[pygame.K_s]: self.camera_pos -= speed * self.camera_front
        if keys[pygame.K_a]: self.camera_pos -= speed * right
        if keys[pygame.K_d]: self.camera_pos += speed * right

        # -- Mouse: accumulate yaw / pitch, derive camera_front --------------
        # get_rel() returns pixels moved since the previous call.
        # Subtracting dy flips the vertical axis: screen Y increases downward
        # but pitch should increase when the mouse moves upward.
        dx, dy = pygame.mouse.get_rel()
        self.yaw   += dx * MOUSE_SENSITIVITY
        self.pitch  = max(-89.0, min(89.0, self.pitch - dy * MOUSE_SENSITIVITY))

        yr = glm.radians(self.yaw)
        pr = glm.radians(self.pitch)
        self.camera_front = glm.normalize(glm.vec3(
            math.cos(yr) * math.cos(pr),
            math.sin(pr),
            math.sin(yr) * math.cos(pr),
        ))

        # -- Build view and projection matrices each frame -------------------
        view = glm.lookAt(
            self.camera_pos,
            self.camera_pos + self.camera_front,
            self.camera_up,
        )
        self.program['u_view'].write(view)

        projection = glm.perspective(glm.radians(self.fov), 800 / 600, 0.1, 100.0)
        self.program['u_projection'].write(projection)

        # -- Draw 10 cubes with fixed tilts ----------------------------------
        self.ctx.clear()
        self.texture.use(location=0)

        for i, pos in enumerate(CUBE_POSITIONS):
            model = glm.translate(glm.mat4(1.0), pos)
            model = glm.rotate(model, glm.radians(20.0 * i), ROTATION_AXIS)
            self.program['u_model'].write(model)
            self.vao.render()


scene = Scene()

# Capture the cursor so it stays confined to the window.
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
# Discard the large initial delta that accumulates before the first frame.
pygame.mouse.get_rel()

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

    # cap delta_time to avoid a huge jump after a stall or the first frame
    delta_time = min(clock.tick() / 1000.0, 0.1)
    scene.render(delta_time)
    pygame.display.flip()

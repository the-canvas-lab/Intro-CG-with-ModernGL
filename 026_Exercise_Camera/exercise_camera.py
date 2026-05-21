# =============================================================================
# Exercise 026 — Camera
# =============================================================================
# Starting point: the free-fly camera from lesson 025.
#
# Tasks
# -----
# 1. FPS-style movement
#    In the lesson the camera can fly in any direction, including straight up
#    or down, because W/S move along camera_front which includes pitch.
#    Modify the keyboard section so that forward/back and strafe always stay
#    on the XZ plane regardless of where the camera is looking.
#    Hint: derive a movement vector that ignores the Y component of camera_front.
#
# 2. Custom LookAt
#    glm.lookAt() hides the matrix construction.  Implement the function stub
#    custom_look_at(pos, target, world_up) so that it produces the same result
#    without calling glm.lookAt(), then wire it in by replacing the
#    glm.lookAt() call in render().
#
#    Steps:
#      a. Compute the forward vector f = normalize(target - pos)
#      b. Compute right r = normalize(cross(f, world_up))
#      c. Compute true up u = cross(r, f)
#      d. Fill the 4x4 view matrix directly using those axes.
#         The matrix maps world coordinates into camera space:
#
#           | r.x   r.y   r.z   -dot(r, pos) |
#           | u.x   u.y   u.z   -dot(u, pos) |
#           | -f.x  -f.y  -f.z   dot(f, pos) |
#           | 0     0     0      1            |
#
#         Remember that pyglm matrices are column-major: m[col][row].
#
# Expected result
# ---------------
# Task 1: moving forward while looking up no longer drifts the camera skyward.
# Task 2: visually identical to the lesson; the cubes look the same because
#         the math inside custom_look_at produces the same matrix as glm.lookAt.
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
CAMERA_SPEED      = 2.5
MOUSE_SENSITIVITY = 0.1


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


# TODO (Task 2): Implement this function.
# Compute f, r, u from pos/target/world_up and build the 4x4 view matrix.
def custom_look_at(pos, target, world_up):
    pass


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

        self.camera_pos   = glm.vec3(0.0, 0.0,  3.0)
        self.camera_front = glm.vec3(0.0, 0.0, -1.0)
        self.camera_up    = glm.vec3(0.0, 1.0,  0.0)
        self.yaw   = -90.0
        self.pitch =   0.0
        self.fov   =  45.0

    def handle_scroll(self, delta_y):
        self.fov = max(1.0, min(45.0, self.fov - delta_y))

    def render(self, delta_time):
        speed = CAMERA_SPEED * delta_time

        # TODO (Task 1): Replace the movement lines below so that W/S/A/D
        # only move on the XZ plane.  Looking up should not lift the camera.
        # Hint: derive a horizontal-only forward vector from camera_front.
        right = glm.normalize(glm.cross(self.camera_front, self.camera_up))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: self.camera_pos += speed * self.camera_front
        if keys[pygame.K_s]: self.camera_pos -= speed * self.camera_front
        if keys[pygame.K_a]: self.camera_pos -= speed * right
        if keys[pygame.K_d]: self.camera_pos += speed * right

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

        # TODO (Task 2): Replace glm.lookAt with custom_look_at once implemented.
        view = glm.lookAt(
            self.camera_pos,
            self.camera_pos + self.camera_front,
            self.camera_up,
        )
        self.program['u_view'].write(view)

        projection = glm.perspective(glm.radians(self.fov), 800 / 600, 0.1, 100.0)
        self.program['u_projection'].write(projection)

        self.ctx.clear()
        self.texture.use(location=0)

        for i, pos in enumerate(CUBE_POSITIONS):
            model = glm.translate(glm.mat4(1.0), pos)
            model = glm.rotate(model, glm.radians(20.0 * i), ROTATION_AXIS)
            self.program['u_model'].write(model)
            self.vao.render()


scene = Scene()

pygame.mouse.set_visible(False)
pygame.event.set_grab(True)
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

    delta_time = min(clock.tick() / 1000.0, 0.1)
    scene.render(delta_time)
    pygame.display.flip()

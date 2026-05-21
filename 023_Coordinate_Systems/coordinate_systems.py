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
# 36 vertices (6 faces × 2 triangles × 3 vertices), each: x y z u v
CUBE_VERTICES = np.array([
    # back face
    -0.5, -0.5, -0.5,  0.0, 0.0,
     0.5, -0.5, -0.5,  1.0, 0.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
    -0.5,  0.5, -0.5,  0.0, 1.0,
    -0.5, -0.5, -0.5,  0.0, 0.0,
    # front face
    -0.5, -0.5,  0.5,  0.0, 0.0,
     0.5, -0.5,  0.5,  1.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 1.0,
     0.5,  0.5,  0.5,  1.0, 1.0,
    -0.5,  0.5,  0.5,  0.0, 1.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,
    # left face
    -0.5,  0.5,  0.5,  1.0, 0.0,
    -0.5,  0.5, -0.5,  1.0, 1.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,
    -0.5,  0.5,  0.5,  1.0, 0.0,
    # right face
     0.5,  0.5,  0.5,  1.0, 0.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
     0.5, -0.5, -0.5,  0.0, 1.0,
     0.5, -0.5, -0.5,  0.0, 1.0,
     0.5, -0.5,  0.5,  0.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 0.0,
    # bottom face
    -0.5, -0.5, -0.5,  0.0, 1.0,
     0.5, -0.5, -0.5,  1.0, 1.0,
     0.5, -0.5,  0.5,  1.0, 0.0,
     0.5, -0.5,  0.5,  1.0, 0.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,
    # top face
    -0.5,  0.5, -0.5,  0.0, 1.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
     0.5,  0.5,  0.5,  1.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 0.0,
    -0.5,  0.5,  0.5,  0.0, 0.0,
    -0.5,  0.5, -0.5,  0.0, 1.0,
], dtype='f4')
# fmt: on


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

        # Depth test: discard fragments hidden behind already-drawn geometry.
        # Without this, a back face can overwrite a front face depending on
        # draw order, causing visible flickering or incorrect surfaces.
        # ctx.clear() resets the depth buffer to 1.0 (maximum depth) each frame.
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

        # Projection does not change frame to frame — upload once.
        # glm.perspective(fov, aspect, near, far) builds a frustum matrix.
        #   fov    : vertical field of view in radians
        #   aspect : window width / height (must match to avoid stretching)
        #   near   : closest visible distance (must be > 0)
        #   far    : farthest visible distance
        projection = glm.perspective(glm.radians(45.0), 800 / 600, 0.1, 100.0)
        self.program['u_projection'].write(projection)

    def render(self, time):
        self.ctx.clear()
        self.texture.use(location=0)

        # --- Model matrix: local space → world space -------------------------
        # Rotates the cube continuously so all six faces become visible.
        model = glm.rotate(glm.mat4(1.0), time, glm.vec3(0.5, 1.0, 0.0))
        self.program['u_model'].write(model)

        # --- View matrix: world space → view/camera space --------------------
        # Moving the camera back along +Z is equivalent to shifting the whole
        # scene forward along -Z. The camera always looks toward -Z by default.
        view = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, -3.0))
        self.program['u_view'].write(view)

        self.vao.render()


scene = Scene()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    time = pygame.time.get_ticks() / 1000.0
    scene.render(time)
    pygame.display.flip()

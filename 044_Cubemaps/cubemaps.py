# =============================================================================
# Lesson 044 — Cubemaps
# =============================================================================
# A cubemap is a texture made of six square faces that together form a cube.
# Sampling it with a 3D direction vector returns the texel on whichever face
# that direction points towards — no UV coordinates needed.
#
# This lesson shows two uses of the same cubemap:
#
#   Skybox — the cubemap faces form the background of the scene.  The cube is
#   rendered at infinite depth by forcing z = w in the vertex shader
#   (gl_Position = pos.xyww), placing it behind all scene geometry.  The view
#   matrix is stripped of its translation component so the skybox stays centred
#   on the camera regardless of position.
#
#   Environment mapping — the cubemap is sampled in the scene fragment shader
#   to simulate reflection and refraction on the surface of the cube.
#
# Modes (← →):
#
#   0 — Textured     Container texture with simple directional lighting.
#   1 — Reflection   Incident ray reflected about the surface normal;
#                    samples the skybox in the mirror direction.
#   2 — Refraction   Incident ray bent through the surface (air-to-glass,
#                    ratio 1/1.52); cube looks like solid glass.
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


def load_cubemap(ctx, folder):
    """Load six face images into a cubemap texture.

    OpenGL cubemap face order: +X right, -X left, +Y top, -Y bottom,
    +Z front, -Z back.  Cubemap faces are not Y-flipped (unlike 2D textures).
    """
    base  = os.path.dirname(os.path.abspath(__file__))
    faces = ['right', 'left', 'top', 'bottom', 'front', 'back']
    images = []
    for face in faces:
        for ext in ('jpg', 'png'):
            path = os.path.join(base, folder, f'{face}.{ext}')
            if os.path.exists(path):
                img = pygame.image.load(path).convert()
                images.append((img.get_size(), pygame.image.tostring(img, 'RGB')))
                break
    size = images[0][0]
    tex  = ctx.texture_cube(size, 3)
    for i, (_, data) in enumerate(images):
        tex.write(face=i, data=data)
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
    return np.ascontiguousarray(np.hstack([verts[:, 5:], verts[:, 2:5], verts[:, 0:2]]))


# Unit cube for the skybox — 36 positions (inside faces visible when camera is
# at the origin).  The position vector is also the cubemap sample direction.
SKYBOX_VERTS = np.array([
    -1.0,  1.0, -1.0,  -1.0, -1.0, -1.0,   1.0, -1.0, -1.0,
     1.0, -1.0, -1.0,   1.0,  1.0, -1.0,  -1.0,  1.0, -1.0,
    -1.0, -1.0,  1.0,  -1.0, -1.0, -1.0,  -1.0,  1.0, -1.0,
    -1.0,  1.0, -1.0,  -1.0,  1.0,  1.0,  -1.0, -1.0,  1.0,
     1.0, -1.0, -1.0,   1.0, -1.0,  1.0,   1.0,  1.0,  1.0,
     1.0,  1.0,  1.0,   1.0,  1.0, -1.0,   1.0, -1.0, -1.0,
    -1.0, -1.0,  1.0,  -1.0,  1.0,  1.0,   1.0,  1.0,  1.0,
     1.0,  1.0,  1.0,   1.0, -1.0,  1.0,  -1.0, -1.0,  1.0,
    -1.0,  1.0, -1.0,  -1.0,  1.0,  1.0,   1.0,  1.0,  1.0,
     1.0,  1.0,  1.0,   1.0,  1.0, -1.0,  -1.0,  1.0, -1.0,
    -1.0, -1.0, -1.0,  -1.0, -1.0,  1.0,   1.0, -1.0, -1.0,
     1.0, -1.0, -1.0,  -1.0, -1.0,  1.0,   1.0, -1.0,  1.0,
], dtype='f4')

MODES = ["Textured", "Reflection", "Refraction"]

CAMERA_POS = glm.vec3(0.0, 0.0, 4.0)


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(moderngl.DEPTH_TEST)

        # --- scene program ---
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
        self.scene_prog['u_texture']    = 0
        self.scene_prog['u_camera_pos'] = CAMERA_POS

        view       = glm.lookAt(CAMERA_POS, glm.vec3(0.0), glm.vec3(0.0, 1.0, 0.0))
        projection = glm.perspective(glm.radians(45.0), 800.0 / 600.0, 0.1, 100.0)
        self.scene_prog['view'].write(view)
        self.scene_prog['projection'].write(projection)

        # Cubemap on unit 1
        cubemap = load_cubemap(self.ctx, '../images/skybox')
        cubemap.use(location=1)
        self.scene_prog['u_skybox'] = 1

        # --- skybox program ---
        self.skybox_prog = self.ctx.program(
            vertex_shader=load_shader('shaders/skybox.vert'),
            fragment_shader=load_shader('shaders/skybox.frag'),
        )
        self.skybox_prog['view'].write(view)
        self.skybox_prog['projection'].write(projection)
        self.skybox_prog['u_skybox'] = 1

        skybox_vbo = self.ctx.buffer(SKYBOX_VERTS.tobytes())
        self.skybox_vao = self.ctx.vertex_array(
            self.skybox_prog,
            [(skybox_vbo, '3f', 'in_position')],
        )

        self.mode = 0
        self._apply_mode()

    def _apply_mode(self):
        self.scene_prog['u_mode'] = self.mode
        label = MODES[self.mode]
        pygame.display.set_caption(
            f"044 — Cubemaps  [{self.mode + 1}/{len(MODES)}] {label}  (← →)"
        )
        print(f"[{self.mode + 1}/{len(MODES)}] {label}")

    def select_mode(self, delta):
        self.mode = (self.mode + delta) % len(MODES)
        self._apply_mode()

    def render(self, time):
        self.ctx.clear(0.1, 0.1, 0.1)

        # --- scene cube ---
        angle = glm.radians(time * 30.0)
        model = glm.rotate(glm.mat4(1.0), angle, glm.vec3(0.0, 1.0, 0.0))
        self.scene_prog['model'].write(model)
        self.scene_prog['normal_matrix'].write(
            glm.mat3(glm.transpose(glm.inverse(model)))
        )
        self.scene_vao.render()

        # --- skybox (rendered last at maximum depth) ---
        # LEQUAL allows the skybox fragments at depth=1.0 to pass the depth
        # test against the cleared depth buffer value of 1.0.
        self.ctx.depth_func = '<='
        self.skybox_vao.render()
        self.ctx.depth_func = '<'


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

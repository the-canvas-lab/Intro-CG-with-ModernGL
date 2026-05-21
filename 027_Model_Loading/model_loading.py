# =============================================================================
# Lesson 027 — Model Loading
# =============================================================================
# Replaces hard-coded vertex arrays with geometry read from a .obj file.
#
# In earlier lessons every cube was defined as 36 rows of hand-written floats.
# That works for a single primitive, but real scenes contain many meshes
# exported from Blender or other 3D tools.  A model loader separates art
# from code: changing the mesh requires only a new .obj file, not an edit here.
#
# OBJ format overview
# -------------------
# An OBJ file stores geometry as plain text:
#
#   v   x y z          -- vertex position
#   vt  u v            -- texture coordinate
#   vn  nx ny nz       -- vertex normal
#   f   v/t/n ...      -- face: one v/t/n triplet per corner
#
# Each face corner references positions, UVs, and normals by independent
# indices.  The same position can appear on multiple faces with different
# normals (e.g., a cube corner shared by three faces).
#
# pywavefront
# -----------
# pywavefront reads the file and produces a flat, interleaved vertex array
# that is ready to be uploaded directly to the GPU.  For a mesh that has
# all three attributes the vertex format is T2F_N3F_V3F:
#
#   u  v  |  nx  ny  nz  |  x  y  z      (8 floats = 32 bytes per vertex)
#
# That layout maps directly to the moderngl format string '2f 3f 3f'.
#
# Note on normals
# ---------------
# The cube.obj includes a normal per face.  Normals are not used by the
# shader in this lesson but in_normal is declared in cube.vert so that:
#   - the VAO descriptor stays consistent with later lighting lessons
#   - no attribute rebinding is needed when we add a lighting shader
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
    data = pygame.image.tostring(image, 'RGBA')
    texture = ctx.texture(image.get_size(), 4, data)
    texture.build_mipmaps()
    return texture


def load_obj(ctx, path):
    """Upload an OBJ file's geometry to the GPU and return a VBO.

    pywavefront merges all face data into material.vertices, a flat Python
    list of floats.  For a mesh with UVs and normals the layout is
    T2F_N3F_V3F:  u v  nx ny nz  x y z  (8 floats per vertex).

    The list is wrapped in a float32 numpy array and written to a GPU buffer.
    """
    base = os.path.dirname(os.path.abspath(__file__))
    scene = pywavefront.Wavefront(
        os.path.join(base, path),
        create_materials=True,
    )

    vertices = []
    for material in scene.materials.values():
        vertices.extend(material.vertices)

    return ctx.buffer(np.array(vertices, dtype='f4'))


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()
        self.ctx.enable(self.ctx.DEPTH_TEST)

        self.program = self.ctx.program(
            vertex_shader=load_shader('shaders/cube.vert'),
            fragment_shader=load_shader('shaders/cube.frag'),
        )

        # Load the cube from an OBJ file.
        # pywavefront produces T2F_N3F_V3F layout (8 floats = 32 bytes/vertex):
        #   '2f'  -- in_uv       (u, v)              bytes  0-7
        #   '12x' -- (skip)      (nx, ny, nz)         bytes  8-19  <- normals skipped here
        #   '3f'  -- in_position (x, y, z)            bytes 20-31
        #
        # '12x' is a stride padding token: 3 floats * 4 bytes = 12 bytes skipped.
        # The normal data is physically present in the buffer and will be bound
        # to 'in_normal' in the lighting lessons when the shader actually uses it.
        vbo = load_obj(self.ctx, '../models/cube.obj')
        self.vao = self.ctx.vertex_array(
            self.program,
            [(vbo, '2f 12x 3f', 'in_uv', 'in_position')],
        )

        self.texture = load_texture(self.ctx, '../images/container.jpg')
        self.program['u_texture'] = 0

        projection = glm.perspective(glm.radians(45.0), 800 / 600, 0.1, 100.0)
        self.program['u_projection'].write(projection)

        view = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, -3.0))
        self.program['u_view'].write(view)

    def render(self, time):
        self.ctx.clear()
        self.texture.use(location=0)

        model = glm.rotate(glm.mat4(1.0), time, glm.vec3(0.5, 1.0, 0.0))
        self.program['u_model'].write(model)
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

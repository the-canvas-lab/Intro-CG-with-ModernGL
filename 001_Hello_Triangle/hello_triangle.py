import math
import os
import sys

import glm
import moderngl
import pygame

os.environ['SDL_WINDOWS_DPI_AWARENESS'] = 'permonitorv2'

pygame.init()
pygame.display.set_mode((800, 600), flags=pygame.OPENGL | pygame.DOUBLEBUF, vsync=True)


class Scene:
    def __init__(self):
        self.ctx = moderngl.get_context()

        self.program = self.ctx.program(
            vertex_shader='''
                #version 330 core

                vec3 vertices[3] = vec3[](
                    vec3(-0.5, -0.5, 0.0),
                    vec3(0.5, -0.5, 0.0),
                    vec3(0.0, 0.5, 0.0)
                );

                void main() {
                    gl_Position = vec4(vertices[gl_VertexID], 1.0);
                }
            ''',
            fragment_shader='''
                #version 330 core

                layout (location = 0) out vec4 out_color;

                void main() {
                    out_color = vec4(1.0, 0.5, 0.2, 1.0);
                }
            ''',
        )

        # A Vertex Array Object (VAO) records how vertex data is laid out in memory
        # and which buffers feed into which shader attributes. When you call render(),
        # the GPU replays that recorded layout automatically — you don't have to
        # re-specify it every frame.
        #
        # Here we pass an empty buffer list [] because the vertex positions are
        # hardcoded inside the vertex shader itself (the `vertices` array), so no
        # CPU-side buffer is needed at all. We only tell the VAO how many vertices
        # to send through the pipeline.
        self.vao = self.ctx.vertex_array(self.program, [])
        self.vao.vertices = 3  # draw 3 vertices → one triangle

    def render(self):
        self.ctx.clear()
        self.ctx.enable(self.ctx.DEPTH_TEST)
        self.vao.render()

scene = Scene()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    scene.render()

    pygame.display.flip()
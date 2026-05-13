# The Graphics Pipeline

Before writing any code, it helps to understand what happens between "a list of vertices" and "pixels on screen." OpenGL processes geometry through a fixed sequence of stages called the **graphics pipeline**.

```
CPU                GPU
───                ───────────────────────────────────────────
vertices ──────▶  Vertex Shader ──▶ Rasterization ──▶ Fragment Shader ──▶ Framebuffer
```

## Vertex Shader

Runs once per vertex. Its job is to compute the final screen position of each vertex by writing to `gl_Position`. This is where transformations (translation, rotation, projection) will eventually live.

## Rasterization

A fixed GPU stage — you don't write code for it. It takes the triangles produced by the vertex shader and determines which pixels they cover, producing one **fragment** per covered pixel.

## Fragment Shader

Runs once per fragment (roughly once per pixel). Its job is to decide the color of that pixel. At this stage the geometry is already fixed; the fragment shader only deals with appearance.

## This Program

This is the simplest possible program that exercises the full pipeline:

- The vertex positions are hardcoded inside the vertex shader as a GLSL array, indexed by `gl_VertexID`. No data is uploaded from the CPU at all.
- The fragment shader outputs a single hardcoded color.
- `moderngl` and `pygame` handle context creation, compilation, and the draw call.

The VAO is created with an empty buffer list `[]` because no CPU-side data is needed — the shader supplies its own vertices.

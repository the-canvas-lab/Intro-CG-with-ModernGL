# Exercise: Two Triangles

This exercise reviews the concepts from programs 001–003.

## What to do

Open `exercise_two_triangles.py` and follow the TODO comments. The shaders are complete — only the vertex data needs to be filled in.

## Concepts reviewed

- Normalized Device Coordinates (NDC): positions must be in the range [-1, 1]
- A single VBO can hold the data for multiple triangles — the GPU processes them as one continuous stream of vertices
- Six vertices = two triangles in a single draw call

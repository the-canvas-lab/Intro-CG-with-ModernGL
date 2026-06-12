# Lesson 047 — Asteroid Field (instanced)

## Run

```
python 047_Asteroids_Instanced/asteroids.py
```

## Controls

| Key | Action |
|-----|--------|
| W A S D | Fly through the scene |
| Mouse | Look around |
| Scroll | Zoom (adjust FOV) |
| Esc | Quit |

## What This Lesson Shows

One planet and 100,000 asteroid rocks, rendered in **2 draw calls total**.

The bottleneck in naive multi-object rendering is CPU-side draw call overhead, not GPU throughput. Without instancing, 100,000 rocks would require 100,000 separate draw calls — the CPU would be the limiting factor. Instancing solves this by uploading all per-instance data (here: model matrices) to a GPU buffer once at startup, then issuing a single draw call.

## Per-instance mat4

A `mat4` is 64 bytes — four `vec4` columns. OpenGL requires each attribute location to hold at most a `vec4`, so the matrix must be split into four separate per-instance attributes:

**Python (upload):**
```python
(inst_vbo, '4f 4f 4f 4f /i', 'in_model_c0', 'in_model_c1',
                              'in_model_c2', 'in_model_c3')
```

**GLSL (reconstruct):**
```glsl
in vec4 in_model_c0, in_model_c1, in_model_c2, in_model_c3;

mat4 model = mat4(in_model_c0, in_model_c1, in_model_c2, in_model_c3);
gl_Position = projection * view * model * vec4(in_position, 1.0);
```

pyglm stores `mat4` in column-major order matching OpenGL convention, so `bytes(m)` gives the raw 64-byte buffer directly.

## Two Shader Programs

The planet and asteroids share the same fragment shader (`object.frag`) but use different vertex shaders:

| Program | Vertex shader | Model matrix source |
|---------|--------------|---------------------|
| `planet_prog` | `planet.vert` | `uniform mat4 model` — set once at startup |
| `asteroid_prog` | `asteroid.vert` | Per-instance `in vec4` columns from the VBO |

## Asteroid Placement

Matches the learnopengl.com 10.3 reference:

```python
angle = i / AMOUNT * 360.0          # evenly spaced — ensures a continuous ring
x = sin(angle) * RING_RADIUS + scatter
y = scatter * 0.4                    # flatten the belt vertically
z = cos(angle) * RING_RADIUS + scatter
scale = rand(0.05, 0.24)
rotate around (0.4, 0.6, 0.8) by a random angle
```

The camera starts at `(0, 0, 155)` — just outside the ring — and uses a free-fly setup (WASD + mouse) from Lesson 025.

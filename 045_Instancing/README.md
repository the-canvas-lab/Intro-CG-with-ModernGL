# Lesson 045 — Instancing

## Run

```
python 045_Instancing/instancing.py
```

## Controls

| Key | Action |
|-----|--------|
| Esc | Quit |

## Core Concept

### The problem: per-draw-call CPU overhead

Every draw call carries a fixed CPU cost — uploading uniforms, binding buffers, driver-side validation. For a few hundred objects this is negligible. For tens of thousands it becomes the bottleneck, leaving the GPU starved while the CPU dispatches calls.

### Instancing: one call, N copies

Instancing renders N copies of the same mesh in a single draw call. Per-instance data (position, color, transform) is stored in a vertex buffer whose attribute **divisor** is set to 1. A divisor of 1 means the GPU advances one element in that buffer per *instance* rather than per vertex — every vertex of instance 0 sees element 0, every vertex of instance 1 sees element 1, and so on.

```python
vao.render(instances=N)
```

### Instance arrays in ModernGL

The `/i` suffix in a vertex array format string sets the divisor to 1 for that buffer binding:

```python
vao = ctx.vertex_array(program, [
    (vertex_vbo, '2f',       'in_position'),           # per-vertex  (divisor 0)
    (inst_vbo,   '2f 3f /i', 'in_offset', 'in_color'), # per-instance (divisor 1)
])
```

Multiple attributes in the same tuple all share the same divisor setting.

### gl_InstanceID

The built-in integer `gl_InstanceID` is available in any vertex shader and counts from 0. It is useful when no per-instance buffer is needed — for example, to look up a value in a uniform array:

```glsl
uniform vec2 offsets[100];
gl_Position = vec4(in_position + offsets[gl_InstanceID], 0.0, 1.0);
```

This approach is simple but limited to the uniform buffer size (~16 KB in base OpenGL 3.3). Instance arrays scale to millions of objects.

## This Lesson

One unit quad (`−0.5..0.5`) is drawn 100 times. Each instance receives a different `in_offset` (NDC position) and `in_color` from the interleaved instance buffer. The vertex shader scales the quad and shifts it to its grid slot:

```glsl
gl_Position = vec4(in_position * 0.08 + in_offset, 0.0, 1.0);
```

See **Lesson 046** for a large-scale application: 100,000 asteroid instances drawn in a single call using per-instance `mat4` model matrices.

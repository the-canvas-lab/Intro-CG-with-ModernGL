# Lesson 048 — Uniform Buffer Objects

## Run

```
python 048_Uniform_Buffer_Objects/ubo.py
```

## Controls

| Key | Action |
|-----|--------|
| Esc | Quit |

## Core Concept

### The problem: duplicated uniform uploads

Every lesson so far set uniforms per program:

```python
prog_a['view'].write(view)
prog_b['view'].write(view)   # same 64 bytes, uploaded again
```

Two programs is tolerable. An engine with 50 shaders updating camera, lights,
fog, and time per frame is not.

### Uniform blocks + binding points

A **Uniform Buffer Object** is an ordinary GPU buffer that shader programs
read through a numbered **binding point**:

```
buffer ──bound to──▶ binding point 0 ◀──reads── program A
                                     ◀──reads── program B
```

In GLSL the uniforms move into a named block:

```glsl
layout (std140) uniform Matrices {
    mat4 view;
    mat4 projection;
};
```

In ModernGL, three steps wire it up:

```python
prog['Matrices'].binding = 0          # program block -> binding point
ubo = ctx.buffer(reserve=128)         # the buffer itself
ubo.bind_to_uniform_block(0)          # buffer -> binding point
```

From then on `ubo.write(...)` updates every program at once.

### std140: the fixed memory layout

`std140` guarantees the same byte layout everywhere, with alignment rules
that surprise everyone once:

| GLSL type | base alignment | consequence |
|-----------|----------------|-------------|
| `float`   | 4 bytes  | packs tightly |
| `vec2`    | 8 bytes  | packs in pairs |
| `vec3`    | **16 bytes** | padded like a vec4! |
| `vec4`    | 16 bytes | as expected |
| `mat4`    | 16 bytes/column | 64 bytes total |

So `vec3 light_dir; vec3 light_color;` occupies bytes 0–11 and **16–27**,
not 12–23. The CPU writes a pad float after each vec3 (see `render()`).
Forgetting this padding is the classic UBO bug: values silently read shifted
garbage, with no error anywhere.

## This Lesson

Four spinning cubes alternate between two programs — diffuse shading
(Phong diffuse, surface normal used) and emissive shading (outputs the
light color directly, surface normal ignored). Both programs share:

- `Matrices` (binding 0): view written once per frame, projection once ever
- `LightBlock` (binding 1): an animated light color whose single buffer
  write visibly recolors objects drawn by *both* programs simultaneously

Per-object data (`model`) deliberately stays a plain uniform: only data
shared across programs belongs in a UBO.

## Why this matters for Vulkan

Vulkan has **no loose uniforms at all**. Every uniform lives in a buffer,
bound through a descriptor set, with std140-style explicit layout — the very
first thing the Vulkan tutorial makes you build is a UBO of exactly this
lesson's `Matrices` block. Learn the layout rules here, where mistakes are
one `print()` away instead of buried under 800 lines of Vulkan boilerplate.

# Lesson 028 — Colors

Introduces the concept of color interaction between a light source and an object surface.

## Run

```
python 028_Colors/colors.py
```

## What you should see

A coral-colored cube at the origin, lit by a small white lamp cube. The lamp orbits around the Y-axis above the object. The object rotates slowly so all faces are visible. Moving the lamp has **no effect** on the object's shading — that is intentional and is addressed in lesson 029.

## Concept

In the real world, objects absorb some wavelengths and reflect others. OpenGL models this as a component-wise multiply:

```glsl
out_color = vec4(u_light_color * u_object_color, 1.0);
```

A white light `(1.0, 1.0, 1.0)` on a coral object `(1.0, 0.5, 0.31)` reflects `(1.0, 0.5, 0.31)`. A red light `(1.0, 0.0, 0.0)` on the same object reflects `(1.0, 0.0, 0.0)` — the green and blue channels are absorbed.

The lamp uses a **separate shader program** so it always renders as its own solid color, unaffected by the lighting calculation.

## Scene setup

| Parameter | Value |
|-----------|-------|
| Camera position | `(0, 4, -6)` looking at origin |
| FOV | 40° |
| Lamp orbit | radius 1.0, height y=2.0, one full revolution per ~6 s |
| Object rotation | 40°/s around axis `(0.5, 1.0, 0.0)` |

## Files

| File | Description |
|------|-------------|
| `colors.py` | Main script; two VAOs sharing one VBO |
| `shaders/object.vert` | MVP transform |
| `shaders/object.frag` | `out_color = light_color * object_color` |
| `shaders/lamp.vert` | MVP transform |
| `shaders/lamp.frag` | Solid white output |
| `../models/cube.obj` | Shared cube geometry |

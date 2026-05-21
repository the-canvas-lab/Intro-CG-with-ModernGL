# Exercise: Multiple Cubes

A single VAO can be drawn many times per frame — just upload a different model matrix before each `vao.render()` call. The view and projection matrices stay the same for all objects; only the model matrix changes.

## What to do

Open `exercise_coordinate_systems.py`. The scene setup (VAO, texture, view, projection) is complete. The render loop iterates over `CUBE_POSITIONS` but uses an identity matrix as a placeholder, so all 10 cubes stack on top of each other at the origin.

## Tasks

### Task 1 — Position and tilt each cube

Inside the loop, build a model matrix that:
- Translates the cube to `pos`
- Rotates it by `glm.radians(20.0 * i)` around `ROTATION_AXIS`

The second operation is applied first (right-to-left), so the cube is rotated around its own centre before being placed at `pos`.

### Task 2 — Animate every third cube

For cubes where `i % 3 == 0` (indices 0, 3, 6, 9), chain an additional rotation by `time` radians around `ROTATION_AXIS`. Append it after the translate so it spins around the cube's own axis rather than orbiting the origin.

## Self-verification

- 10 cubes visible at various distances and depths
- Each cube has a different fixed tilt (Task 1)
- Cubes at indices 0, 3, 6, 9 spin; the others hold still (Task 2)
- Depth ordering looks correct — nearer cubes occlude farther ones

## Concepts reviewed

- Reusing one VAO for multiple draw calls with different model matrices
- Composing translate + rotate for in-place rotation at an offset position
- Per-object vs per-frame matrix updates

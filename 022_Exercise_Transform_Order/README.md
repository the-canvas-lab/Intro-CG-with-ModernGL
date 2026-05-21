# Exercise: Transform Order

Matrix multiplication is **not commutative** — `T × R ≠ R × T`. This exercise makes that difference visible by changing the order of two operations and watching the motion change.

## What to do

Open `exercise_transform_order.py`.

## Tasks

### Task 1 — Swap rotate and translate

The first quad currently builds its matrix as **T × R × S** (translate written first in code, applied last). Swap the translate and rotate lines so the matrix becomes **R × T × S** instead.

Run the program and compare the two behaviours:

| Matrix order | Code order | Effect on geometry |
|---|---|---|
| T × R × S | translate, rotate, scale | Quad **spins in place** at (0.5, −0.5) |
| R × T × S | rotate, translate, scale | Quad **orbits** around the world origin |

Why the difference? With **R × T × S**, the quad is first scaled, then moved to (0.5, −0.5), and finally that already-offset position is rotated around (0, 0) — so it traces a circle.

### Task 2 — Second quad with sin() scaling

Uncomment the second quad's render block at the bottom of `render()` and fill in its transform:

- Translate to `(-0.5, 0.5, 0.0)` (top-left area)
- Scale by `(sin(time), sin(time), 1.0)` — no rotation needed

`math.sin(time)` is already imported. Note that `sin()` passes through zero and goes negative — when the scale factor is negative the image inverts. This is intentional and identical to Blender's behaviour when a negative scale is applied to a mesh.

## Self-verification

- Task 1: quad traces a circular path (orbiting), not spinning in place
- Task 2: a second quad appears at the top-left and pulses — growing, shrinking, and periodically flipping

## Concepts reviewed

- Transformation order and its geometric meaning
- Building compound transforms with pyglm
- Using `sin()` as a time-driven scale factor

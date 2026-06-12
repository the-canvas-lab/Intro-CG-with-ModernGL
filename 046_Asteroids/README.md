# Lesson 046 — Asteroid Field (no instancing)

## Run

```
python 046_Asteroids/asteroids.py
```

## Controls

| Key | Action |
|-----|--------|
| W A S D | Fly through the scene |
| Mouse | Look around |
| Scroll | Zoom (adjust FOV) |
| Esc | Quit |

## What This Lesson Shows

One planet and 1,000 asteroid rocks, drawn in **1,001 separate draw calls**.

This is the naive approach: for each asteroid the CPU writes a `uniform mat4 model` and issues a draw call. The bottleneck is not GPU throughput — it is CPU-side draw call overhead. Each call carries fixed cost (driver state validation, command encoding) that compounds quickly.

At 1,000 rocks the frame time is already higher than it should be for a scene this simple. Compare with Lesson 047, which renders **100× more rocks** (100,000) in just **2 draw calls** using instancing.

## Render Loop

```python
# Planet — 1 draw call
prog['model'].write(planet_matrix)
planet_vao.render()

# Asteroid belt — AMOUNT draw calls (one per rock)
for m in matrices:
    prog['model'].write(m)
    asteroid_vao.render()
```

## Why This Doesn't Scale

| Rocks | Draw calls | Approach |
|------:|----------:|---------|
| 1,000 | 1,001 | This lesson — noticeably CPU-bound |
| 100,000 | 100,001 | Unrunnable on most hardware |
| 100,000 | **2** | Lesson 047 with instancing |

The driver validates GPU state on every draw call regardless of how small the mesh is. With 1,000 calls per frame at 60 fps that is 60,000 driver round-trips per second — all CPU work with no GPU benefit.

## Asteroid Placement

Identical to Lesson 047 — evenly distributed angles, random scatter displacement, y flattened by 0.4, scale 0.05–0.24, rotation around `(0.4, 0.6, 0.8)`.

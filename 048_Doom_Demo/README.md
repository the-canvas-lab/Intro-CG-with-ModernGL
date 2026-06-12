# Lesson 048 — Doom Demo (capstone)

## Run

```
python 048_Doom_Demo/doom_demo.py
```

## Controls

| Input | Action |
|-------|--------|
| W A S D | Move (locked to the floor) |
| Mouse | Turn (yaw only — like the original Doom) |
| Left click | Shoot |
| Esc | Quit |

**Goal:** slay all 5 imps lurking in the maze before they claw you down.

## Why a Doom clone?

Doom (1993) is the canonical proof that a compelling 3D game needs only a
handful of rendering techniques — and by lesson 047 you have learned all of
them. This capstone assembles the course into one playable demo:

| Game feature | Lesson it comes from |
|---|---|
| Textured walls / floor / ceiling | 016–020 — textures, UV tiling |
| Maze baked from a text grid | 023–024 — world-space geometry, model matrices |
| FPS camera locked to the floor | 025–026 — `lookAt`, XZ-plane movement |
| Flashlight following the camera | 036–037 — spot light cone + attenuation |
| Enemies as 2D billboard sprites | 039 — alpha cutout via `discard` |
| Sprites always facing the player | 021 — rotate-Y model matrix per frame |
| Retro chunky pixel look | 018 — NEAREST filtering on low-res art |
| HUD: gun, crosshair, health, damage flash | 040 — alpha blending |
| Walls vs. sprites depth ordering | 038 — depth testing |

## What is genuinely new

Only game *logic*, not graphics:

### The map is data

The maze is a list of strings (`#` wall, `.` floor, `P` player, `E` enemy).
At startup `build_world_mesh()` walks the grid and emits world-space
triangles — but **only wall faces that border an open cell**, since interior
faces could never be seen. Because the world never moves, there is no model
matrix at all: the vertex shader consumes world coordinates directly.
Edit the `MAP` strings and the level rebuilds itself.

### Grid collision

`try_move()` attempts the X and Z components of a movement separately, each
validated with a four-corner check against the wall grid. Blocking one axis
while allowing the other is what makes the player *slide* along a wall
instead of sticking to it — a trick used by virtually every FPS since.

### Hit-scan shooting

A shot is not a projectile. `shoot()` marches along the view ray until it
hits a wall cell, then picks the nearest living enemy whose center lies
within `HIT_RADIUS` of the ray *and* in front of that wall. The same
ray-sampling helper (`line_of_sight`) doubles as enemy vision.

### Billboarding

Each enemy is a flat textured quad rotated about Y so it always faces the
camera: `angle = atan2(to_cam.x, to_cam.z)`. This is exactly how Doom
"rendered 3D monsters" — there were never any 3D monsters.

### Procedural sprite art

The imp, its corpse, and the pistol are drawn at startup with `pygame.draw`
onto small `SRCALPHA` surfaces and uploaded with **NEAREST** filtering, so
the lesson needs no external image assets and keeps the chunky retro look.

## Things to try

- Edit the `MAP` strings — build your own level, add more `E`s.
- Make imps need two shots: give `Enemy` an `hp` attribute.
- Widen/narrow the flashlight cone (`light.cut_off` angles) — fear scales
  inversely with cone width.
- Add the lesson 042 framebuffer pipeline and a red vignette post-effect
  that grows as health drops.

# Lesson 025 — Camera

Adds a free-fly camera controlled by keyboard and mouse.

## Run

```
python 025_Camera/camera.py
```

## Controls

| Input | Action |
|-------|--------|
| W / S | Move forward / backward |
| A / D | Strafe left / right |
| Mouse | Look around |
| Scroll | Zoom in / out |
| Esc | Quit |

## Concepts

**Camera vectors** — the view matrix is rebuilt every frame from three live vectors:

- `camera_pos` — where the camera sits in world space
- `camera_front` — unit vector in the direction the camera looks
- `camera_up` — world-space up direction `(0, 1, 0)`

`glm.lookAt(camera_pos, camera_pos + camera_front, camera_up)` constructs the view matrix from those vectors.

**WASD movement** — each frame the camera position is displaced along `camera_front` (forward/back) or the right vector `cross(camera_front, camera_up)` (strafe). Displacement is multiplied by `delta_time` so speed is frame-rate-independent.

**Mouse look** — relative mouse motion (`pygame.mouse.get_rel()`) accumulates into two Euler angles: `yaw` (horizontal) and `pitch` (vertical). `camera_front` is reconstructed from those angles each frame:

```python
camera_front = normalize(vec3(
    cos(yaw) * cos(pitch),
    sin(pitch),
    sin(yaw) * cos(pitch),
))
```

Pitch is clamped to ±89° to avoid a singularity when looking straight up or down.

**Scroll zoom** — adjusts the perspective FOV. Smaller FOV zooms in; larger FOV shows more of the scene.

**delta_time** — `clock.tick() / 1000.0`, capped at 0.1 s to avoid a large jump after a stall or on the first frame.

## Files

| File | Description |
|------|-------------|
| `camera.py` | Main script |
| `shaders/cube.vert` | MVP transform |
| `shaders/cube.frag` | Texture sample |

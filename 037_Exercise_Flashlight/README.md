# Exercise 037 — Flashlight

Attach the spot light from lesson 036 to the camera so it always illuminates whatever the player is looking at, then add interactive cone control.

## Run

```
python 037_Exercise_Flashlight/exercise_flashlight.py
```

Before the TODOs are filled in, the scene is completely black and the cone size is fixed. After, moving and looking around reveals the containers lit by the beam, and ↑ / ↓ widens or narrows it.

## Controls

| Key / Input | Action |
|-------------|--------|
| WASD | Move forward / back / left / right |
| Mouse | Look |
| ↑ / ↓ | Widen / narrow the beam |
| Esc | Quit |

## Tasks

Both TODOs are in `exercise_flashlight.py`. The fragment shader does not need to change.

### TODO 1 — `render()`: follow the camera

The `Light` struct has `position` and `direction` uniforms. Think about what camera state maps to each, and upload them every frame.

### TODO 2 — `adjust_cone(delta)`: resize the beam

`self.cone_angle` holds the inner half-angle in degrees. The outer cone is always 2.5° wider. Clamp the angle to a sensible range, then upload `light.cut_off` and `light.outer_cut_off` — the shader expects cosines, not degrees.

## What to observe

- TODO 1: the beam follows your view as you look around.
- TODO 2: ↑ gradually reveals more of the scene; ↓ narrows it back to a tight spot. Notice how the soft edge (the 2.5° gap between inner and outer cone) becomes more or less noticeable at different widths.

## Files

| File | Description |
|------|-------------|
| `exercise_flashlight.py` | Main script — **TODO 1** and **TODO 2** here |
| `shaders/object.frag` | Complete spot light shader (provided, identical to solution) |
| `shaders/object.vert` | Passes position, normal, UV |

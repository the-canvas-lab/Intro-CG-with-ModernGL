# Exercise 031 — Gouraud Shading (split-screen)

The window is split into two equal panels showing the same scene simultaneously:

| Panel | Shading | Status |
|-------|---------|--------|
| Left (0–399 px) | Phong — computed per fragment | Provided (reference) |
| Right (400–799 px) | Gouraud — computed per vertex | Your TODO |

## Run

```
python 031_Exercise_Gouraud/exercise_gouraud.py
```

Before the TODOs are filled in, the right panel renders magenta (placeholder color). Implement the two shader TODOs until both panels show the lit coral cube, then compare them side by side.

## Background

**Phong shading** evaluates the full ambient + diffuse + specular equation once per fragment — every pixel gets an exact lighting value. Highlights are smooth and accurate.

**Gouraud shading** evaluates the same equation once per vertex. The GPU then linearly interpolates the resulting color across each triangle. It is cheaper but the specular highlight appears banded or can vanish entirely if the brightest point falls between triangle vertices.

A cube is a coarse mesh — 8 corners, large flat faces — which makes the Gouraud artifact easy to see. Watch the specular highlight cross a face boundary as the lamp orbits.

## Tasks

Both TODOs are inside `shaders/gouraud_object.vert` and `shaders/gouraud_object.frag`. The Python file does **not** need to change.

### shaders/gouraud_object.vert

1. Declare an output varying above `main()`:
   ```glsl
   out vec3 gouraud_color;
   ```

2. After `frag_pos` and `norm` are computed, add the Phong equations (same as `phong_object.frag`). Store the result:
   ```glsl
   gouraud_color = (ambient + diffuse + specular) * u_object_color;
   ```

### shaders/gouraud_object.frag

1. Declare the matching input:
   ```glsl
   in vec3 gouraud_color;
   ```

2. Replace the magenta placeholder:
   ```glsl
   out_color = vec4(gouraud_color, 1.0);
   ```

## Expected result

Both panels look similar, but the right panel's specular highlight shifts abruptly at face boundaries rather than fading smoothly. The artifact is most visible when the lamp is close to a face edge.

The solution is not provided — implement it using the Phong equations from `030_Phong_Components`.

## Files

| File | Description |
|------|-------------|
| `exercise_gouraud.py` | Split-view main script; no changes needed |
| `shaders/phong_object.vert` | Reference Phong vertex shader (provided) |
| `shaders/phong_object.frag` | Reference Phong fragment shader (provided) |
| `shaders/gouraud_object.vert` | **TODO** — compute Phong here, in the vertex stage |
| `shaders/gouraud_object.frag` | **TODO** — pass the interpolated color through |
| `shaders/lamp.vert` / `lamp.frag` | Lamp cube (unchanged) |

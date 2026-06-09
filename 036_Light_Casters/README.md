# Lesson 036 — Light Casters

Three light types in one scene. Press ← / → to cycle through them and compare their behaviour directly.

## Run

```
python 036_Light_Casters/light_casters.py
```

## Controls

| Key | Action |
|-----|--------|
| → / ← | Cycle through light types |
| Esc | Quit |

## Light types

| Mode | Type | Key property |
|------|------|-------------|
| 1 | Directional | No position; same direction for every fragment; no attenuation |
| 2 | Point | Position; brightness falls with distance |
| 3 | Spot | Position + cone; fragments outside the cone receive ambient only |

## What to observe

The directional angle, the point light position, and the spot light position are all set to the same apparent location `(2, 3, 2)` so the shading direction is identical when you first switch modes. The differences are isolated:

- **Directional → Point**: near cubes brighten, far cubes dim — attenuation kicking in. The lamp cube appears to show the source position.
- **Point → Spot**: most cubes go dark — same position, but now restricted to a cone. Only the cubes within ~20–25° of the beam centre stay lit.

## Shader design

A single `Light` struct carries all fields; `u_mode` selects which branch runs:

```glsl
if (u_mode == 0) {
    // Directional
    light_dir = normalize(-light.direction);

} else if (u_mode == 1) {
    // Point — adds attenuation
    light_dir   = normalize(light.position - frag_pos);
    float d     = length(light.position - frag_pos);
    attenuation = 1.0 / (light.constant + light.linear * d + light.quadratic * d * d);

} else {
    // Spot — adds cone intensity
    light_dir     = normalize(light.position - frag_pos);
    float theta   = dot(light_dir, normalize(-light.direction));
    float epsilon = light.cut_off - light.outer_cut_off;
    intensity     = clamp((theta - light.outer_cut_off) / epsilon, 0.0, 1.0);
}
```

## Files

| File | Description |
|------|-------------|
| `light_casters.py` | Main script; all light parameters set once, `u_mode` changes on key press |
| `shaders/object.frag` | Combined Phong shader with mode branch |
| `shaders/object.vert` | Passes position, normal, UV |
| `shaders/lamp.vert` / `lamp.frag` | Lamp cube (shown in Point and Spot modes only) |

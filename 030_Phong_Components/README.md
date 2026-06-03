# Lesson 030 — Phong Component Decomposition

The Phong model sums three terms: ambient + diffuse + specular. This lesson lets you inspect each component in isolation by pressing ← / → before seeing the full result.

## Run

```
python 030_Phong_Components/phong_components.py
```

## Controls

| Key | Action |
|-----|--------|
| → / ← | Cycle through modes |
| Esc | Quit |

| # | Mode | What you see |
|---|------|-------------|
| 1 | Ambient | Flat, constant base color — does not change as the lamp moves |
| 2 | Diffuse | Smooth shading that follows the lamp — bright face-on, dark side-on |
| 3 | Specular | Only the highlight — watch it travel across the cube as the lamp orbits |
| 4 | Full Phong | All three summed — the final result |

## What to observe

- **Ambient** is view- and position-independent — it lifts the whole surface uniformly regardless of where the lamp is.
- **Diffuse** changes with lamp angle but not with your viewing angle.
- **Specular** changes with both lamp angle and viewing angle — it is the only component that depends on where the camera is.
- The lamp orbits continuously so you can watch how each component responds to a moving light source.

## Key code — `shaders/object.frag`

```glsl
// Ambient: constant base light
vec3 ambient = light.ambient * material.ambient;

// Diffuse: brightness proportional to how directly the surface faces the lamp
vec3 norm      = normalize(normal);
vec3 light_dir = normalize(light.position - frag_pos);
float diff     = max(dot(norm, light_dir), 0.0);
vec3 diffuse   = light.diffuse * (diff * material.diffuse);

// Specular: mirror-like highlight, visible when the reflected ray points toward the viewer
vec3 view_dir    = normalize(u_view_pos - frag_pos);
vec3 reflect_dir = reflect(-light_dir, norm);
float spec       = pow(max(dot(view_dir, reflect_dir), 0.0), material.shininess);
vec3 specular    = light.specular * (spec * material.specular);
```

## Files

| File | Description |
|------|-------------|
| `phong_components.py` | Main script |
| `shaders/object.frag` | Phong calculation with mode selector |
| `shaders/object.vert` | Passes `frag_pos` and `normal` to the fragment stage |
| `shaders/lamp.vert` / `lamp.frag` | Lamp cube |

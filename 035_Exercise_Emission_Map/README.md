# Exercise 035 — Emission Map

Extend the lighting maps scene from lesson 034 by adding an emission map that makes the container glow with a matrix-style pattern, independent of any light source.

## Run

```
python 035_Exercise_Emission_Map/exercise_emission_map.py
```

Before the TODOs are filled in, the scene looks identical to lesson 034 — no glow. After, the emission pattern from `container2_emission.png` will appear on the container regardless of where the lamp is.

## Background

An emission map stores the color a surface emits by itself. Unlike diffuse or specular, emission is not affected by the light position, the surface normal, or the viewing angle — it is simply added to the final color:

```glsl
out_color = vec4(ambient + diffuse + specular + emission, 1.0);
```

This makes emission useful for glowing UI panels, neon signs, lava, or any surface that should appear self-lit.

## Tasks

### TODO 1 — `shaders/object.frag`: add the emission field to the Material struct

```glsl
struct Material {
    sampler2D diffuse;
    sampler2D specular;
    sampler2D emission;   // ← add this
    float     shininess;
};
```

### TODO 2 — `shaders/object.frag`: sample, mask, and add the emission contribution

```glsl
vec3 emission = vec3(texture(material.emission, tex_coords));
out_color = vec4(ambient + diffuse + specular + emission, 1.0);
```

### TODO 3 — `exercise_emission_map.py`: load the texture and wire it up

```python
self.emission_tex = load_texture(self.ctx, '../images/container2_emission.png')
self.emission_tex.use(location=2)
# ...
self.object_program['material.emission'] = 2
```

## What to observe

- The emission glow is visible even on faces fully in shadow (facing away from the lamp), because emission is independent of the light.
- Moving the lamp does not change where the glow appears, but the specular highlight on the metal frame still moves normally.

## Files

| File | Description |
|------|-------------|
| `exercise_emission_map.py` | Main script — **TODO 3** here |
| `shaders/object.frag` | Fragment shader — **TODO 1** and **TODO 2** here |
| `shaders/object.vert` | Unchanged from lesson 034 |
| `shaders/lamp.vert` / `lamp.frag` | Lamp cube (unchanged) |

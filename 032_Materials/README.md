# Lesson 032 — Materials

Replaces the single object color with a **Material** struct that gives each surface independent ambient, diffuse, specular, and shininess properties.

## Run

```
python 032_Materials/materials.py
```

## What you should see

A cyan plastic cube under a white light. The cube has a bright specular highlight characteristic of plastic. Try changing `ACTIVE_MATERIAL` in `materials.py` to `MATERIAL_EMERALD` or `MATERIAL_GOLD` to see how dramatically different the same light looks on different materials.

## GLSL structs

The fragment shader uses two structs:

```glsl
struct Material {
    vec3  ambient;    // color reflected under ambient light
    vec3  diffuse;    // color reflected under diffuse light
    vec3  specular;   // color of the specular highlight
    float shininess;  // exponent that controls highlight sharpness
};

struct Light {
    vec3 position;
    vec3 ambient;   // intensity of the ambient component
    vec3 diffuse;   // intensity of the diffuse component
    vec3 specular;  // intensity of the specular component
};
```

Struct fields are set by dotting into the uniform name from Python:

```python
program['material.ambient']   = m['ambient']
program['material.shininess'] = m['shininess']
program['light.ambient']      = (0.2, 0.2, 0.2)
```

## Why separate light intensities?

Using `(1,1,1)` for all three light components makes objects unrealistically bright. Real scenes have much dimmer ambient light than direct illumination:

| Component | Value used |
|-----------|-----------|
| `light.ambient` | `(0.2, 0.2, 0.2)` — dim fill |
| `light.diffuse` | `(0.5, 0.5, 0.5)` — moderate direct |
| `light.specular` | `(1.0, 1.0, 1.0)` — full highlights |

## Material presets

| Name | Description |
|------|-------------|
| `MATERIAL_EMERALD` | Deep green with bright specular |
| `MATERIAL_GOLD` | Warm yellow-orange tones |
| `MATERIAL_CYAN_PLASTIC` | Cold blue-green, moderate shininess |

Values from http://devernay.free.fr/cours/opengl/materials.html

## Files

| File | Description |
|------|-------------|
| `materials.py` | Main script; `ACTIVE_MATERIAL` selects the preset |
| `shaders/object.vert` | Transforms position and normal |
| `shaders/object.frag` | Phong with `Material` and `Light` structs |
| `shaders/lamp.vert` | MVP transform only |
| `shaders/lamp.frag` | Solid white output |

# Lesson 032 — Material Selector

Extends lesson 031 by preloading an array of 8 material definitions to the GPU and switching between them at runtime with a single integer uniform.

## Run

```
python 032_Material_Selector/material_selector.py
```

## Controls

| Key | Action |
|-----|--------|
| → | Next material |
| ← | Previous material |
| Esc | Quit |

The active material name and index are shown in the window title bar.

## New concepts

### GLSL uniform arrays

You can declare an array of structs as a uniform:

```glsl
const int NUM_MATERIALS = 8;

struct Material {
    vec3  ambient;
    vec3  diffuse;
    vec3  specular;
    float shininess;
};

uniform Material materials[NUM_MATERIALS];
uniform int      u_material_index;
```

All 8 materials live on the GPU for the lifetime of the program. Switching only requires updating one integer.

### Uploading array elements from Python

Each struct field is addressed by its index in the array name:

```python
for i, (_, mat) in enumerate(MATERIALS):
    program[f'materials[{i}].ambient']   = mat['ambient']
    program[f'materials[{i}].diffuse']   = mat['diffuse']
    program[f'materials[{i}].specular']  = mat['specular']
    program[f'materials[{i}].shininess'] = mat['shininess']
```

### Dynamic array indexing

The fragment shader selects the active material using a non-constant index — valid in GLSL 3.30:

```glsl
Material mat = materials[u_material_index];
```

### Integer uniform

```python
program['u_material_index'] = self.material_index  # plain Python int
```

## Why this pattern matters

Preloading a data array to the GPU and selecting entries with an index is a general GPU programming pattern. The same idea scales up to:

- **Uniform Buffer Objects (UBOs)** — larger arrays without the per-field upload overhead
- **Texture arrays** — selecting a texture layer by index
- **Instanced rendering** — per-instance data stored in a buffer, indexed by `gl_InstanceID`

## Materials included

| # | Name | Character |
|---|------|-----------|
| 1 | Emerald | Deep green, bright specular |
| 2 | Gold | Warm yellow, tight highlight |
| 3 | Ruby | Deep red, bright specular |
| 4 | Pearl | Pale pink, wide soft highlight |
| 5 | Obsidian | Dark purple-grey, moderate specular |
| 6 | Chrome | Neutral grey, very bright tight highlight |
| 7 | Bronze | Warm brown-orange, soft specular |
| 8 | Cyan Plastic | Cold blue-green, moderate shininess |

Values from http://devernay.free.fr/cours/opengl/materials.html

## Files

| File | Description |
|------|-------------|
| `material_selector.py` | Main script |
| `shaders/object.vert` | Transforms position and normal |
| `shaders/object.frag` | Phong lighting; indexes `materials[u_material_index]` |
| `shaders/lamp.vert` / `lamp.frag` | Lamp cube |

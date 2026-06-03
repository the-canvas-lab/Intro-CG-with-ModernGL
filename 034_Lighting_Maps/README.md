# Lesson 034 — Lighting Maps

Replaces the uniform material color vectors from lesson 032 with two textures that give each fragment its own lighting properties.

## Run

```
python 034_Lighting_Maps/lighting_maps.py
```

## What you should see

A container cube rotating under an orbiting white lamp. The wooden face panels absorb the specular highlight while the metal edges and corners reflect it brightly — because the specular map encodes that difference per pixel.

## Concept

In lesson 032, the material held three `vec3` values for ambient, diffuse, and specular. Every fragment on the surface used the same values, producing a uniform appearance. Lighting maps replace those with textures:

| Uniform (lesson 032) | Texture (this lesson) | What it controls |
|----------------------|-----------------------|-----------------|
| `material.ambient`   | (reuses diffuse map)  | base lift        |
| `material.diffuse`   | `material.diffuse`    | per-pixel color  |
| `material.specular`  | `material.specular`   | per-pixel highlight intensity |

The struct in GLSL changes accordingly:

```glsl
// Before (lesson 032)
struct Material {
    vec3  ambient;
    vec3  diffuse;
    vec3  specular;
    float shininess;
};

// After (this lesson)
struct Material {
    sampler2D diffuse;   // replaces ambient + diffuse
    sampler2D specular;
    float     shininess;
};
```

## Key code — `shaders/object.frag`

```glsl
vec3 diff_color = vec3(texture(material.diffuse,  tex_coords));
vec3 spec_color = vec3(texture(material.specular, tex_coords));

vec3 ambient  = light.ambient  * diff_color;
vec3 diffuse  = light.diffuse  * diff * diff_color;
vec3 specular = light.specular * spec * spec_color;
```

## Binding textures from Python

Textures are uploaded to specific units and the shader is told which unit number to sample from:

```python
diffuse_tex.use(location=0)
specular_tex.use(location=1)

program['material.diffuse']  = 0  # unit index, not a color
program['material.specular'] = 1
```

## Vertex data

The vertex buffer now carries UV coordinates alongside position and normal. `load_obj_mesh()` extracts all three from the T2F_N3F_V3F pywavefront layout:

```python
pos = verts[:, 5:]   # x y z
nrm = verts[:, 2:5]  # nx ny nz
uv  = verts[:, 0:2]  # u v
```

The VAO format string grows to `'3f 3f 2f'` and the vertex shader gains `in vec2 in_uv`.

## Files

| File | Description |
|------|-------------|
| `lighting_maps.py` | Main script; loads both textures and sets `material.diffuse/specular` to unit indices |
| `shaders/object.vert` | Passes `frag_pos`, `normal`, and `tex_coords` to the fragment stage |
| `shaders/object.frag` | Samples diffuse and specular maps; `Material` struct uses `sampler2D` |
| `shaders/lamp.vert` / `lamp.frag` | Lamp cube (unchanged) |

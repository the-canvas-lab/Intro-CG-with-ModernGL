# Lesson 029 — Basic Lighting (Phong)

Implements the Phong lighting model in the fragment shader: ambient + diffuse + specular.

## Run

```
python 029_Basic_Lighting/basic_lighting.py
```

## What you should see

A coral cube that is brightest where the lamp faces it and darker on the sides turned away. A specular highlight moves as the lamp orbits. The lamp itself stays white regardless of the shading model.

## Phong lighting

All three components are computed per fragment in `object.frag`:

**Ambient** — constant base light so unlit faces aren't completely black:
```glsl
vec3 ambient = 0.1 * u_light_color;
```

**Diffuse** — depends on the angle between the surface normal and the light direction (Lambert's cosine law):
```glsl
float diff    = max(dot(norm, light_dir), 0.0);
vec3  diffuse = diff * u_light_color;
```

**Specular** — mirror-like highlight; depends on the angle between the reflected ray and the view direction:
```glsl
vec3  reflect_dir = reflect(-light_dir, norm);
float spec        = pow(max(dot(view_dir, reflect_dir), 0.0), 32.0);
vec3  specular    = 0.5 * spec * u_light_color;
```

## Normal matrix

Surface normals must be transformed with a special matrix — not the model matrix — to stay perpendicular to the surface after non-uniform scaling:

```python
normal_matrix = glm.mat3(glm.transpose(glm.inverse(model)))
```

For pure rotation (no scaling) this equals the model matrix, but computing it correctly handles the general case.

## Buffer layout

The VBO stores interleaved `[x, y, z, nx, ny, nz]` (6 floats per vertex):

```python
# Object VAO reads both position and normal:
object_vao = ctx.vertex_array(prog, [(vbo, '3f 3f', 'in_position', 'in_normal')])

# Lamp VAO reads only position, skipping the 12-byte normal:
lamp_vao   = ctx.vertex_array(prog, [(vbo, '3f 12x', 'in_position')])
```

## Files

| File | Description |
|------|-------------|
| `basic_lighting.py` | Main script |
| `shaders/object.vert` | Transforms position and normal to world space |
| `shaders/object.frag` | Full Phong: ambient + diffuse + specular |
| `shaders/lamp.vert` | MVP transform only |
| `shaders/lamp.frag` | Solid white output |
| `../models/cube.obj` | Shared cube geometry |

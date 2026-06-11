# Lesson 044 — Cubemaps

## Run

```
python 044_Cubemaps/cubemaps.py
```

## Controls

| Key | Action |
|-----|--------|
| ← / → | Cycle mode |
| Esc | Quit |

## Modes

| # | Mode | Description |
|---|------|-------------|
| 1 | Textured | Container texture with directional lighting |
| 2 | Reflection | Cube surface mirrors the surrounding skybox |
| 3 | Refraction | Cube surface bends light like glass (ratio 1/1.52) |

## Core Concept

### What is a cubemap?

A cubemap is a texture made of six square faces that together form a cube. Instead of UV coordinates, it is sampled with a 3D direction vector — the GPU looks up whichever face and texel that direction points towards. The GLSL sampler type is `samplerCube` and the sampling function is the usual `texture()`.

```glsl
uniform samplerCube u_skybox;
out_color = texture(u_skybox, some_direction);
```

### Loading a cubemap

Six face images are uploaded in OpenGL's fixed order: +X (right), −X (left), +Y (top), −Y (bottom), +Z (front), −Z (back). Unlike 2D textures, cubemap faces are **not** Y-flipped.

```python
tex = ctx.texture_cube(size, components=3)
for i, face_data in enumerate(faces):
    tex.write(face=i, data=face_data)
```

### Skybox

The skybox is a large cube that surrounds the entire scene. The vertex position is used directly as the cubemap sample direction — no UV coordinates are needed. Two tricks ensure it always appears at infinite distance behind all geometry:

**1 — Strip translation from the view matrix.**  
`mat4(mat3(view))` zeroes the translation column, keeping only rotation. The skybox stays centred on the camera regardless of where the camera moves.

```glsl
vec4 pos = projection * mat4(mat3(view)) * vec4(in_position, 1.0);
```

**2 — Force depth to 1.0.**  
After the perspective divide, `z / w = 1.0` (the far plane). Assigning `z = w` before the divide achieves this:

```glsl
gl_Position = pos.xyww;   // x=x, y=y, z=w, w=w → depth = 1.0
```

The skybox is drawn **last**. The depth function is temporarily changed to `LEQUAL` (`<=`) so the skybox fragments at depth 1.0 pass the test against the cleared depth buffer (which is also 1.0). After rendering, the function is restored to `LESS`.

```python
ctx.depth_func = '<='
skybox_vao.render()
ctx.depth_func = '<'
```

### Environment mapping

Both reflection and refraction sample the same skybox cubemap using the world-space surface normal and the incident ray from the camera.

**Reflection** — the `reflect()` function mirrors the incident ray `I` about the surface normal `N`:

```glsl
vec3 I = normalize(frag_pos - u_camera_pos);
vec3 R = reflect(I, N);
out_color = vec4(texture(u_skybox, R).rgb, 1.0);
```

**Refraction** — `refract()` bends the ray as it crosses the surface boundary. The ratio is `n1 / n2` (Snell's law). For air-to-glass, `n_air ≈ 1.0` and `n_glass ≈ 1.52`:

```glsl
vec3 R = refract(I, N, 1.0 / 1.52);
out_color = vec4(texture(u_skybox, R).rgb, 1.0);
```

Both effects require world-space inputs, so the vertex shader outputs `frag_pos` (world-space position) and the normal is transformed by the normal matrix rather than the full model matrix.

## Code

### Two shader programs

| Program | Vertex shader | Fragment shader | Purpose |
|---------|--------------|-----------------|---------|
| `scene_prog` | `scene.vert` | `scene.frag` | Rotating cube (3 modes) |
| `skybox_prog` | `skybox.vert` | `skybox.frag` | Background skybox |

### Texture units

| Unit | Content |
|------|---------|
| 0 | `container2.png` (2D texture for mode 0) |
| 1 | Skybox cubemap (used by both programs) |

The cubemap is bound to unit 1 and the sampler uniform is set to 1 in both programs, so neither program needs to rebind the texture each frame.

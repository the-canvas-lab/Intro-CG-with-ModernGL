# Lesson 038 — Depth Testing

## Run

```
python 038_Depth_Testing/depth_testing.py
```

Press ← / → to cycle through the three modes while the program is running.

## Controls

| Key | Action |
|-----|--------|
| ← / → | Switch mode |
| Esc | Quit |

## Core Concept

### The depth buffer

Every pixel on screen has a corresponding entry in the **depth buffer** (also called the z-buffer). Before a fragment is written to the color buffer, the GPU compares its depth value against what is already stored. If the new fragment is closer, it wins and both the color and depth buffers are updated; otherwise the fragment is discarded. This is what makes closer objects correctly occlude farther ones without sorting geometry on the CPU.

The depth value stored is a single float in **[0, 1]**, where 0 maps to the near plane and 1 to the far plane.

### Non-linear distribution

You might expect the depth buffer to store distance linearly — a cube halfway between near and far gets 0.5. It does not. The value actually stored comes from the perspective projection matrix and is proportional to **1/z** (view-space distance):

```
depth = A + B / z_view
```

where A and B are constants derived from near and far. This means:

- The region from the near plane to a short distance ahead gets the majority of the available precision.
- The rest of the depth range is compressed into a thin band near 1.0.

With `near = 0.1` and `far = 100.0`, the 10 cubes in this scene are 5–12 units from the camera. Their raw depth values are all in the range **0.981–0.993** — less than 2% of the full [0, 1] range. In mode 1 they appear nearly uniform white, which directly shows the compression.

This non-linearity is intentional: it gives high precision where it matters most (objects close to the camera, where small depth differences are visually significant) and sacrifices precision far away (where objects are small on screen and tiny depth differences are invisible). The trade-off breaks down when two distant coplanar surfaces compete for the same depth values, causing **z-fighting**.

### Linearizing depth for visualization

To recover a value proportional to actual distance, apply the inverse of the perspective depth formula:

```
z_ndc    = depth * 2.0 - 1.0                          // [0,1] → NDC [-1,1]
z_linear = (2 * near * far) / (far + near - z_ndc * (far - near))
```

`z_linear` is now the view-space distance in world units. Dividing by `far` normalizes it back to [0, 1] for display. In mode 2 the same cubes show a clear gradient — the closest cube (5 units away) is noticeably darker than the farthest (12 units away).

## Modes

| Mode | What you see | Why |
|------|-------------|-----|
| 0 — Normal | Textured shading | Reference: identifies which parts of the image correspond to which cubes |
| 1 — Depth (raw) | `gl_FragCoord.z` as grayscale | All cubes appear nearly white — the 1/z compression leaves very little visible difference across the scene |
| 2 — Depth (linear) | Linearized depth / far | Clear near-to-far gradient; shows where the actual distance information is |

## Code

### `depth_testing.py`

`NEAR` and `FAR` are defined as module-level constants and passed to both `glm.perspective()` and the shader uniforms `u_near` / `u_far`. Keeping them in one place ensures the projection matrix and the linearization formula always agree.

```python
NEAR =   0.1
FAR  = 100.0
...
projection = glm.perspective(glm.radians(45.0), 800.0 / 600.0, NEAR, FAR)
self.program['u_near'] = NEAR
self.program['u_far']  = FAR
```

### `shaders/object.frag`

**Mode 0** — standard shading: a fixed directional light gives the cubes enough shape to serve as a reference.

**Mode 1** — raw depth: `gl_FragCoord.z` is a built-in that gives the depth buffer value [0, 1] for the current fragment. Writing it directly to all three color channels produces a grayscale image of the depth buffer.

```glsl
out_color = vec4(vec3(gl_FragCoord.z), 1.0);
```

**Mode 2** — linearized depth: convert from [0, 1] to NDC, apply the inverse perspective formula, then normalize by `far`.

```glsl
float z_ndc  = gl_FragCoord.z * 2.0 - 1.0;
float linear = (2.0 * u_near * u_far) / (u_far + u_near - z_ndc * (u_far - u_near));
out_color    = vec4(vec3(linear / u_far), 1.0);
```

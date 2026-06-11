# Lesson 042 — Framebuffers

## Run

```
python 042_Framebuffers/framebuffers.py
```

## Controls

| Key | Action |
|-----|--------|
| ← / → | Cycle post-processing effect |
| Esc | Quit |

## Core Concept

### What is a Framebuffer Object?

Normally every draw call writes directly to the default framebuffer — the window. A Framebuffer Object (FBO) is an offscreen render target: a colour texture (and optional depth buffer) that the GPU writes to instead. Once the scene is rendered into it, that texture can be read and manipulated like any other texture.

This enables a two-pass rendering pipeline:

```
Pass 1:  scene geometry  →  FBO colour texture
Pass 2:  full-screen quad  →  window  (samples FBO texture, applies effect)
```

### FBO setup

```python
color_tex = ctx.texture((W, H), 4)            # RGBA texture — the render target
depth_buf = ctx.depth_renderbuffer((W, H))    # depth storage (not sampled, just needed for depth test)
fbo       = ctx.framebuffer(
    color_attachments=[color_tex],
    depth_attachment=depth_buf,
)
```

The colour attachment is a plain `moderngl.Texture`. After Pass 1 it contains the rendered scene and can be bound to a sampler unit like any texture.

### Two-pass render loop

```python
# Pass 1 — render into the FBO
fbo.use()
ctx.enable(moderngl.DEPTH_TEST)
ctx.clear(...)
draw_scene(...)

# Pass 2 — draw the result onto the screen with a post-processing effect
ctx.screen.use()
ctx.disable(moderngl.DEPTH_TEST)   # screen quad doesn't need depth
color_tex.use(location=1)
draw_screen_quad(...)
```

`ctx.screen.use()` switches back to the default (window) framebuffer. Depth testing is disabled for Pass 2 because the quad always covers the full screen and there is nothing to occlude.

### Screen quad

The screen quad is two triangles in Normalised Device Coordinates (NDC), covering the full clip-space rectangle from (-1, -1) to (1, 1). The vertex shader is a passthrough — position and UV go straight to `gl_Position` and the interpolator:

```glsl
gl_Position = vec4(in_position, 0.0, 1.0);
```

No MVP matrices are needed; the geometry is already in clip space.

### Post-processing effects

All effects are implemented in the fragment shader by sampling `u_screen` (the FBO colour texture) at `tex_coords`:

| Mode | Effect |
|------|--------|
| 0 — None | `texture(u_screen, tex_coords)` — unmodified scene |
| 1 — Inversion | `1.0 - col` — flip each channel around 0.5 |
| 2 — Grayscale | `dot(col, vec3(0.2126, 0.7152, 0.0722))` — ITU-R BT.601 luminance |
| 3 — Sharpen | 3×3 convolution with centre weight +9, neighbours −1 |
| 4 — Blur | 3×3 box filter (each weight 1/9) |
| 5 — Edge Detection | Laplacian kernel (centre −8, all neighbours +1) |

Convolution effects sample the texture at the 8 surrounding pixels using a fixed `OFFSET = 1/300` in UV space, accumulating a weighted sum:

```glsl
vec3 sample_kernel(float kernel[9]) {
    vec3 col = vec3(0.0);
    for (int i = 0; i < 9; i++)
        col += texture(u_screen, tex_coords + offsets[i]).rgb * kernel[i];
    return col;
}
```

## Code

### Texture unit assignment

The scene texture (container2.png) is bound to unit 0. The FBO colour texture is bound to unit 1. Keeping them on separate units avoids rebinding the scene texture each frame.

```python
load_texture(ctx, '...container2.png').use(location=0)
scene_prog['u_texture'] = 0

color_tex.use(location=1)
screen_prog['u_screen'] = 1
```

### Normal matrix

The scene fragment shader uses a simple directional light, so the normal must be transformed from local space to world space. A non-uniform scale distorts normals if the model matrix is used directly; the normal matrix corrects this:

```python
self.scene_prog['normal_matrix'].write(
    glm.mat3(glm.transpose(glm.inverse(model)))
)
```

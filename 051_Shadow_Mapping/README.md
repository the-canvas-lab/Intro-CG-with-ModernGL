# Lesson 051 — Shadow Mapping

## Run

```
python 051_Shadow_Mapping/shadow_mapping.py
```

## Controls

| Input | Action |
|-------|--------|
| W A S D | Move camera |
| Mouse | Look |
| B | Toggle depth bias (off → shadow acne) |
| P | Toggle PCF soft edges |
| Space | Pause the orbiting light |
| Esc | Quit |

## Core Concept

### Rasterization can't see occluders

When a fragment is shaded, the pipeline knows nothing about geometry between
it and the light — each triangle is processed in isolation. Shadow mapping
recovers that information by *asking the light*:

```
PASS 1 (light's view)                 PASS 2 (camera's view)
render depth-only into a FBO    →     project each fragment into light
"shadow map": nearest surface         space; if the map recorded something
the light sees, per direction         NEARER, the fragment is in shadow
```

It is a pure remix of earlier lessons: a depth buffer (038) rendered into an
offscreen framebuffer (042), looked up through one extra matrix transform
(023). The overlay in the bottom-right corner shows pass 1's raw output.

### The light-space matrix

For a directional light, "the light's camera" is an **orthographic** box
(all rays parallel) aimed at the scene:

```python
light_space = glm.ortho(-14, 14, -14, 14, 1, 40) * glm.lookAt(light_pos, center, up)
```

Pass 2 transforms each world-space fragment by this same matrix, divides by
`w`, remaps from NDC to `[0,1]`, and compares `p.z` against the stored depth
at `p.xy`. Fragments outside the box are treated as lit.

### Shadow acne (press B)

The map has finite resolution, so a surface sampled at an angle zig-zags
above and below its own recorded depth — and shadows *itself* in moiré
stripes. The standard fix is a small depth **bias**, scaled up at grazing
angles:

```glsl
float bias = max(0.05 * (1.0 - dot(n, l)), 0.005);
```

Too much bias causes the opposite artifact ("peter-panning": shadows detach
from their objects' feet) — bias tuning is a permanent fact of life in
real-time shadows.

### PCF (press P)

One depth comparison per fragment gives hard, aliased shadow edges at the
shadow map's resolution. **Percentage-closer filtering** samples a 3×3
neighbourhood and averages the *comparison results* (not the depths — an
averaged depth is meaningless), giving fractional shadow values and softer
edges.

### Implementation notes (ModernGL)

- `ctx.depth_texture(size)` + `ctx.framebuffer(depth_attachment=...)` builds
  the depth-only FBO; the pass-1 fragment shader is literally empty.
- Depth textures default to comparison ("shadow sampler") mode; set
  `compare_func = ''` to sample raw depth values with a regular `sampler2D`.
- Pass 1 reuses the same VBOs with a position-only attribute layout
  (`'3f 5x4'` skips the normal + UV bytes — the stride/offset idea from 010).

## Why this matters before Vulkan

Shadow mapping is the canonical **multi-pass** technique: two render passes,
a depth attachment consumed as a texture, and per-pass pipeline state. That
is precisely the shape of Vulkan's render-pass/attachment machinery, so it
pays to have done it once where the API overhead is three lines instead of
three hundred.

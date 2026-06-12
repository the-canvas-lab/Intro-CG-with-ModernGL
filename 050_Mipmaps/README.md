# Lesson 050 — Mipmaps

## Run

```
python 050_Mipmaps/mipmaps.py
```

## Controls

| Key | Action |
|-----|--------|
| ← / → | Switch filtering mode |
| Esc | Quit |

## Core Concept

### Minification: the other half of filtering

Lesson 018 magnified a texture (NEAREST vs LINEAR). This lesson is the
opposite problem: a floor receding to the horizon squeezes *thousands* of
texels into each distant pixel. A `texture()` call samples only a couple of
them — massive undersampling — and the result shimmers and forms moiré
patterns the moment the camera moves (mode 1).

### The mip chain

A mipmapped texture stores pre-shrunk copies, each half the size of the
last: 256 → 128 → 64 → … → 1. Every texel of level *n* is the average of
4 texels of level *n−1*, so a distant pixel can sample a level where the
averaging has already been done correctly. `build_mipmaps()` — which the
lessons have called since 016 without comment — generates this chain.
Total memory cost: just **+33%** (¼ + ¹⁄₁₆ + … = ⅓).

The GPU picks the level automatically from the screen-space UV derivatives
(how fast the texture coordinates change between adjacent pixels). The
fragment shader does nothing special.

### Min-filter modes

The minification filter has the form *texel-filter* `_MIPMAP_` *level-filter*:

| Mode | Behaviour |
|------|-----------|
| `LINEAR` | no mipmaps; full shimmer |
| `LINEAR_MIPMAP_NEAREST` | snap to nearest level — visible bands where the level switches |
| `LINEAR_MIPMAP_LINEAR` | blend the two nearest levels — **trilinear**, smooth |

### The debug X-ray (mode 4)

Mode 4 overwrites each mip level with a solid color (level 0 red, 1 orange,
2 yellow, …) via `texture.write(data, level=n)`. The floor turns into a
literal map of which level the GPU samples at which distance — the single
most clarifying picture of how mipmapping works.

## Why this matters for Vulkan

Vulkan has no `build_mipmaps()`. You specify `mipLevels` when creating the
image, then fill each level yourself by recording a chain of `vkCmdBlitImage`
calls, transitioning layouts level by level. That chapter of the Vulkan
tutorial is purely mechanical *if* you already know what the chain is, what
the levels contain, and what min-filter modes select — which is this lesson.

# Lesson 049 — Gamma Correction

## Run

```
python 049_Gamma_Correction/gamma_correction.py
```

## Controls

| Key | Action |
|-----|--------|
| Space | Toggle gamma correction on/off |
| Esc | Quit |

## Core Concept

### Monitors are not linear

A display does not emit light proportionally to the pixel value it is given:
it applies a power curve of roughly **2.2**. A pixel value of 0.5 emits only
about 22% as much light as 1.0. Historically this matched CRT physics;
today it survives because it conveniently matches human brightness
perception (sRGB).

This breaks lighting math in two directions:

1. **Output**: every lighting result we computed in lessons 028–037 was
   silently darkened by the display. Diffuse terms, attenuation — all warped.
2. **Input**: textures are painted *on* gamma displays, so their stored
   values are sRGB-encoded. Sampling one gives perceptual values, not light
   intensities. Lighting them without decoding double-applies the curve.

### The correct pipeline

```
sRGB texture --decode--> linear --[all lighting math]--> linear --encode--> display
              pow(2.2)                                            pow(1/2.2)
```

Decode once at sampling, encode once at the very end — never in between, and
never twice (washed-out output is the classic symptom of double encoding).

### Physically-correct attenuation suddenly works

In gamma space, the inverse-square law `1/d²` looks far too dark, which is
why pre-gamma-era engines used `1/d` or the constant/linear/quadratic rig
from lesson 036. In linear space, `1/d²` simply looks right. Toggle Space
and watch the three light pools: same physics, different space.

### The gradient strip

The strip across the top renders a mathematically linear ramp. Uncorrected,
its apparent midpoint sits around 73% of the way along; corrected, halfway
along really looks half as bright.

## In practice (and in Vulkan)

Real engines don't call `pow()` — they declare textures with an `SRGB`
internal format (free decode on sampling) and render into an `SRGB`
framebuffer (free encode on write). In Vulkan you cannot avoid the topic:
choosing the swapchain image format (`VK_FORMAT_B8G8R8A8_SRGB` vs `_UNORM`)
is one of the first lines of code you write, and picking wrong makes
everything too dark or washed out. After this lesson you'll know exactly
which symptom means which mistake.

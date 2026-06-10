# Lesson 040 — Blending

## Run

```
python 040_Blending/blending.py
```

## Controls

| Key | Action |
|-----|--------|
| Esc | Quit |

## Core Concept

### How blending works

Alpha blending lets a fragment composite with whatever is already in the framebuffer rather than replacing it. Enable it with two lines on the CPU side:

```python
ctx.enable(moderngl.BLEND)
ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
```

This sets the blend equation to:

```
result = src_alpha × src_color + (1 − src_alpha) × dst_color
```

Where `src` is the incoming fragment and `dst` is what is already in the framebuffer. At `src_alpha = 1.0` the result is the source color unchanged; at `src_alpha = 0.0` it is invisible; in between it is a weighted mix.

The fragment shader does nothing special — it simply outputs the full RGBA value from the texture. The GPU blend unit handles the compositing automatically.

### Render order

Blending reads from the destination framebuffer, so what is already there matters. The required order is:

1. **Opaque geometry first.** Transparent objects need something to blend against. Drawing the wall first ensures the framebuffer is populated before any window is composited over it.
2. **Transparent objects back-to-front.** Each window composites over everything already drawn. If the front window were drawn first, the back window's fragments would fail the depth test (the front window already wrote its depth) and the overlap region would show only the front window, with the back window invisible behind it.

With two windows the order is hardcoded. A general scene with many transparent objects would require sorting by distance from the camera every frame, which is expensive and still breaks down for intersecting geometry. This is why **alpha cutout** (`discard`, lesson 039) is preferred whenever hard-edged transparency is acceptable.

## Scene

| Object | Position | Depth |
|--------|----------|-------|
| Wall (opaque) | z = −5 | furthest |
| Back window | center x = −0.75, z = −2 | middle |
| Front window | center x = +0.75, z = 0 | closest |

Both windows are the same landscape size (1.2 × 0.8 before model scale). Shifting them horizontally by ±0.75 creates a partial overlap in the centre where the front window composites over the back window, which in turn composites over the wall — showing all three blend layers at once.

## Code

### Single program, two textures

Both the wall and the windows use the same shader. Switching between them is a single `.use()` call before each draw:

```python
self.wall_tex.use(location=0)
self.program['model'].write(self.wall_model)
self.vao.render()

self.window_tex.use(location=0)
for model in self.window_models:
    self.program['model'].write(model)
    self.vao.render()
```

### Model matrix for sizing and placement

All objects share one unit quad (`−1..1`). Size and position are encoded entirely in the model matrix:

```python
def make_model(pos, scale):
    return glm.scale(glm.translate(glm.mat4(1.0), pos), scale)

self.wall_model = make_model(glm.vec3(0.0, 0.0, -5.0), glm.vec3(8.0, 6.0, 1.0))

WIN = glm.vec3(1.2, 0.8, 1.0)
self.window_models = [
    make_model(glm.vec3(-0.75, 0.0, -2.0), WIN),  # back
    make_model(glm.vec3( 0.75, 0.0,  0.0), WIN),  # front
]
```

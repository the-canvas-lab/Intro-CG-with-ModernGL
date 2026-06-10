# Lesson 039 — Discarding Fragments

## Run

```
python 039_Discarding_Fragments/discarding_fragments.py
```

## Controls

| Key | Action |
|-----|--------|
| Esc | Quit |

## Core Concept

### The problem with transparent sprites

A grass sprite is an RGBA texture where the grass blades are opaque and the surrounding area is fully transparent. If you render it as a plain textured quad, the GPU writes every fragment — including the transparent background — to the color buffer. The result is a solid rectangle with black or white corners sitting on top of the scene.

### The fix: `discard`

The fragment shader can exit early and produce **no output at all** using the `discard` keyword:

```glsl
vec4 tex_color = texture(u_texture, tex_coords);
if (tex_color.a < 0.1)
    discard;
out_color = tex_color;
```

A discarded fragment is completely removed from the pipeline — no color write, no depth write. The pixels where the background was transparent simply remain whatever was already in the framebuffer, revealing objects behind the sprite correctly.

### Why no depth sorting is needed

True alpha blending requires geometry to be drawn back-to-front so that semi-transparent surfaces composite correctly. `discard` avoids this entirely: every fragment is either fully opaque (written normally) or fully gone. There is no semi-transparency and therefore no order dependency. This makes it ideal for vegetation, fences, and any "cutout" geometry.

### Texture clamping

```python
grass_tex.repeat_x = False
grass_tex.repeat_y = False
```

By default, textures repeat — UV values outside [0, 1] wrap around. Setting `repeat = False` switches to `GL_CLAMP_TO_EDGE`, which prevents floating-point imprecision near UV edges from sampling a non-transparent border texel and leaving a faint coloured fringe around the sprite.

## Code

### Two programs, one vertex shader

The floor (solid brown) and the grass (textured, with discard) share `object.vert` but have separate fragment shaders. The floor vertices include dummy UV coordinates so they are compatible with the shared vertex layout.

```python
vert = load_shader('shaders/object.vert')
self.floor_program = self.ctx.program(vertex_shader=vert,
                                      fragment_shader=load_shader('shaders/floor.frag'))
self.grass_program = self.ctx.program(vertex_shader=vert,
                                      fragment_shader=load_shader('shaders/grass.frag'))
```

### Grass quad geometry

Each grass blade is a unit quad (1 wide, 1 tall) with its base at `y = 0`, facing `+z`. Individual blades are placed in the world with a translation matrix:

```python
self.grass_models = [glm.translate(glm.mat4(1.0), p) for p in GRASS_POSITIONS]
```

### Render order

The floor is drawn first, then each grass blade. Because discarded fragments leave depth untouched, overlapping blades still occlude each other correctly without any sorting.

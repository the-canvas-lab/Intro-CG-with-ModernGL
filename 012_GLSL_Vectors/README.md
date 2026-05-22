# GLSL Vectors and Swizzling

GLSL has built-in vector types that make shader arithmetic concise. Understanding them is essential for everything from color manipulation to transformations.

## Vector Types

| Type | Components | Typical use |
|------|-----------|-------------|
| `vec2` | x, y | 2D positions, texture coordinates |
| `vec3` | x, y, z | 3D positions, RGB colors |
| `vec4` | x, y, z, w | Homogeneous positions, RGBA colors |

## Component Access

Components can be accessed by position (`.x .y .z .w`) or by color alias (`.r .g .b .a`) — they refer to the same underlying data:

```glsl
vec3 v = vec3(1.0, 2.0, 3.0);
float a = v.x;    // 1.0
float b = v.r;    // also 1.0 — same component, different name
```

## Swizzling

Any combination of components can be selected and reordered in a single expression:

```glsl
vec3 v = vec3(1.0, 2.0, 3.0);
vec2 xy  = v.xy;       // (1.0, 2.0)
vec3 bgr = v.bgr;      // (3.0, 2.0, 1.0) — reversed
vec3 rrr = v.rrr;      // (1.0, 1.0, 1.0) — repeated
```

## Vector Construction

Vectors can be built from scalars, smaller vectors, or a mix:

```glsl
vec4 color = vec4(v.rgb, 1.0);   // vec3 + float → vec4
vec3 pos   = vec3(p.xy, 0.0);      // vec2 + float → vec3
```

## This Program

The vertex shader derives the fragment color entirely from the vertex position using component access and swizzling — no color data in the buffer at all. Compare the shader to the verbose version you may have written in exercise 011.

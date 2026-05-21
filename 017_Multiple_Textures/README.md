# Multiple Textures

A single draw call can sample from more than one texture simultaneously. Each texture is bound to a different **texture unit**, and the fragment shader holds one `sampler2D` uniform per texture pointing at the corresponding unit number.

## Binding Multiple Units

```python
texture0.use(location=0)
texture1.use(location=1)

program['u_texture0'] = 0
program['u_texture1'] = 1
```

Both textures are active at the same time. The GPU can access up to 16 texture units (`GL_TEXTURE0`–`GL_TEXTURE15`) within a single draw call.

## Blending in the Fragment Shader

GLSL's built-in `mix(a, b, t)` linearly interpolates between two values:

```
mix(a, b, t) = a * (1 - t) + b * t
```

At `t = 0` only `a` is visible; at `t = 1` only `b` is visible; at `t = 0.5` they blend equally.

```glsl
uniform sampler2D u_texture0;
uniform sampler2D u_texture1;

void main() {
    out_color = mix(texture(u_texture0, uv), texture(u_texture1, uv), 0.2);
}
```

## This Program

`container.jpg` and `awesomeface.png` are both sampled at the same UV and blended with `mix()` at a fixed ratio of 0.2 — the container image dominates at 80% while the face is 20% visible.

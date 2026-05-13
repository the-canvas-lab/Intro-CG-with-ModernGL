# Uniforms

Vertex attributes (like `in_position`) differ per vertex — they are read from the buffer once per vertex shader invocation. A **uniform** is different: it is set once from the CPU and holds the same value for every vertex and fragment processed in a single draw call.

## Declaring and Setting

In GLSL:
```glsl
uniform float u_time;
```

In Python (moderngl looks up the uniform by name):
```python
program['u_time'] = 1.5
```

The value persists until you change it — setting it once before `vao.render()` is enough.

## Uniforms vs Vertex Attributes

| | Vertex attribute | Uniform |
|---|---|---|
| Source | Buffer (VBO) | CPU assignment |
| Value | Different per vertex | Same for all vertices |
| Typical use | Position, color, UV | Time, color, transform matrix |

## This Program

A `float` uniform `u_time` is updated every frame with the elapsed time in seconds. The fragment shader uses `sin(u_time)` to animate the green channel of the triangle's color. The animation makes it obvious that the CPU is sending a new value to the GPU each frame.

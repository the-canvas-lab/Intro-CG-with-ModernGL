# Multiple Shader Programs

Program 007 used one shader program for both objects. To give each object a different appearance — different color, different shading model — each needs its own shader program.

## One Program Per Appearance

A shader **program** is a linked pair of vertex and fragment shaders. You can share the vertex shader source between programs while swapping only the fragment shader:

```python
vert = load_shader('shaders/triangle.vert')

program1 = ctx.program(vertex_shader=vert,
                       fragment_shader=load_shader('shaders/triangle_orange.frag'))
program2 = ctx.program(vertex_shader=vert,
                       fragment_shader=load_shader('shaders/triangle_blue.frag'))
```

The vertex shader source is shared on the CPU but each program compiles it independently — they are fully separate GPU pipelines.

## Connecting Programs to VAOs

Each VAO is bound to its own program at creation time:

```python
vao1 = ctx.vertex_array(program1, [(vbo1, '3f', 'in_position')])
vao2 = ctx.vertex_array(program2, [(vbo2, '3f', 'in_position')])
```

Calling `vao1.render()` automatically uses `program1`; `vao2.render()` uses `program2`. No manual program switching is needed.

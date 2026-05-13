# Multiple Objects

So far every program has rendered a single piece of geometry. Real scenes contain many independent objects. The key idea is that each object owns its own VAO and VBO — they are completely independent of one another.

## One VAO/VBO Per Object

```python
vbo1 = ctx.buffer(vertices1)
vao1 = ctx.vertex_array(program, [(vbo1, '3f', 'in_position')])

vbo2 = ctx.buffer(vertices2)
vao2 = ctx.vertex_array(program, [(vbo2, '3f', 'in_position')])
```

Modifying or deleting one object's buffer has no effect on the other. This maps directly to the raw OpenGL pattern of generating multiple VAO/VBO handles — moderngl just removes the manual bind/unbind.

## Rendering

```python
vao1.render()
vao2.render()
```

Each `.render()` call is self-contained. There is no global "currently bound VAO" state to manage, unlike raw OpenGL.

## This Program

Two triangles, one on each side of the screen, each with its own VBO and VAO, rendered with the same shader program.

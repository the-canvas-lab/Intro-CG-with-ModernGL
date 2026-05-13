# Index Buffer Object (IBO)

Program 005 stored the rectangle as six vertices, repeating the two diagonal corners. An **index buffer** eliminates that duplication by letting you reference vertices by index rather than repeating their data.

## How It Works

Instead of six vertices, you store four unique ones and a separate list of indices:

```
Vertices (4):          Indices (6):
0: top right           0, 1, 3   ← triangle 1
1: bottom right        1, 2, 3   ← triangle 2
2: bottom left
3: top left
```

The GPU looks up each index in the vertex buffer to assemble the triangles. Vertices 1 and 3 are stored once but referenced twice — saving memory and bandwidth.

## In moderngl

```python
ibo = ctx.buffer(np.array([0, 1, 3, 1, 2, 3], dtype='i4'))

vao = ctx.vertex_array(
    program,
    [(vbo, '3f', 'in_position')],
    index_buffer=ibo,
    index_element_size=4,    # 4 bytes per index → dtype='i4'
)
```

`index_element_size=4` tells the GPU each index is a 32-bit integer (matching `dtype='i4'`). The draw call is identical — `vao.render()` automatically uses `glDrawElements` instead of `glDrawArrays`.

## Why It Matters

The saving is small for a rectangle, but for a mesh with thousands of shared edges the index buffer can cut vertex data in half or more.

# Vertex Buffer Object (VBO)

In program 002 the vertex positions were still hardcoded inside the GLSL shader. This is convenient for a fixed triangle but impractical for any real geometry — you can't change the positions without recompiling the shader.

## Uploading Data to the GPU

A **Vertex Buffer Object (VBO)** is a block of memory that lives on the GPU. You create it by uploading a NumPy array from the CPU:

```python
vertices = np.array([...], dtype='f4')   # CPU-side array
vbo = ctx.buffer(vertices)               # upload to GPU memory
```

After the upload the CPU array can be discarded. The GPU reads directly from the VBO during rendering.

## Connecting the Buffer to the Shader

The VAO records how the buffer is laid out and which shader attribute receives each piece of data:

```python
vao = ctx.vertex_array(program, [(vbo, '3f', 'in_position')])
```

- `'3f'` — each attribute is 3 consecutive 32-bit floats
- `'in_position'` — maps to `in vec3 in_position` in the vertex shader

The GPU reads 3 floats at a time from the VBO and delivers them as `in_position` to each vertex shader invocation.

## This Program

Same triangle as before, but the positions now come from a CPU array rather than the shader source. The shader is reduced to a single `in vec3 in_position` attribute — it no longer knows anything about the geometry itself.

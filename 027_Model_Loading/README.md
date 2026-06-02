# Lesson 027 — Model Loading

Replaces hard-coded vertex arrays with geometry read from a `.obj` file using **pywavefront**.

## Run

```
python 027_Model_Loading/model_loading.py
```

## What you should see

A single textured cube (container.jpg) rotating around axis `(0.5, 1.0, 0.0)`. The geometry is identical to earlier lessons but now comes from `models/cube.obj`.

## OBJ format overview

An OBJ file stores geometry as plain text:

```
v   x y z          # vertex position
vt  u v            # texture coordinate
vn  nx ny nz       # vertex normal
f   v/t/n ...      # face: one v/t/n triplet per corner
```

Each face corner references positions, UVs, and normals by independent indices. The same position can appear on multiple faces with different normals (e.g. a cube corner shared by three faces).

## pywavefront T2F_N3F_V3F layout

pywavefront reads the file and produces a flat, interleaved vertex array. For a mesh with all three attributes the per-vertex layout is:

```
u  v | nx  ny  nz | x  y  z      (8 floats = 32 bytes per vertex)
```

This maps to the moderngl format string `'2f 3f 3f'`. In this lesson the normals are present in the buffer but skipped by the VAO descriptor with `'12x'` (12 bytes = 3 floats × 4 bytes):

```python
vao = ctx.vertex_array(program, [(vbo, '2f 12x 3f', 'in_uv', 'in_position')])
```

The normals stay in the buffer unchanged so later lighting lessons can bind them without changing the geometry data.

## Files

| File | Description |
|------|-------------|
| `model_loading.py` | Main script with `load_obj()` helper |
| `shaders/cube.vert` | MVP transform + UV pass-through |
| `shaders/cube.frag` | Texture sample |
| `../models/cube.obj` | Unit cube geometry |
| `../images/container.jpg` | Diffuse texture |

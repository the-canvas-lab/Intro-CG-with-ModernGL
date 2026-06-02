# Exercise 033 — Material Grid

Starting point: lesson 032 (Material Selector).

Instead of displaying one material at a time, render all 8 materials simultaneously as a **4×2 grid** so they can be compared side by side under identical lighting.

## Run

```
python 033_Exercise_Material_Grid/exercise_material_grid.py
```

Before the TODOs are filled in, only the lamp cube renders — the object loop does nothing. After completing the tasks you should see 8 lit cubes in two rows.

## Task

Everything is in `render()`. The loop skeleton and all constants are provided; you fill in the body.

```python
for i in range(len(MATERIALS)):
    # 1. Compute grid position
    col = i % COLS
    row = i // COLS
    x   = (col - (COLS - 1) / 2.0) * SPACING
    y   = (row - (ROWS - 1) / 2.0) * SPACING

    # 2. Build model matrix — rotate in place, then translate to grid cell
    model = glm.translate(glm.mat4(1.0), glm.vec3(x, y, 0.0)) * SHARED_ROTATION

    # 3. Select this cube's material before drawing
    self.object_program['u_material_index'] = i

    # 4. Upload and render
    self.object_program['model'].write(model)
    self.object_vao.render()
```

Note: `SHARED_NORMAL_MATRIX` is already uploaded once before the loop — it is the same for every cube, so there is no need to re-upload it per draw call.

## Key concept

`u_material_index` is set **between draw calls**, not inside the shader. The GPU sees a fresh uniform value for each cube even though the same VAO and shader program are used every time. This is the fundamental pattern behind material systems in game engines.

The solution is in `034_Solution_Material_Grid/`.

## Files

| File | Description |
|------|-------------|
| `exercise_material_grid.py` | Starter code — fill in `render()` |
| `shaders/object.vert` | Unchanged from 032 |
| `shaders/object.frag` | Unchanged from 032 — indexes `materials[u_material_index]` |
| `shaders/lamp.vert` / `lamp.frag` | Lamp cube |

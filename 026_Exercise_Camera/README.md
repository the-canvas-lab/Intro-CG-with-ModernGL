# Exercise 026 — Camera

Starting point: the free-fly camera from lesson 025.

## Run

```
python 026_Exercise_Camera/exercise_camera.py
```

## Tasks

### Task 1 — FPS-style movement

In lesson 025 the camera can fly in any direction, including straight up or down, because W/S move along `camera_front` which includes the pitch angle.

Modify the keyboard section so that forward/back and strafe always stay on the XZ plane regardless of where the camera is looking.

**Hint:** derive a horizontal-only forward vector that ignores the Y component of `camera_front`:

```python
# Zero the Y component and re-normalize — the result points horizontally
# in whatever direction the camera is facing.
forward_xz = glm.normalize(glm.vec3(camera_front.x, 0.0, camera_front.z))
```

**Expected result:** moving forward while looking up no longer drifts the camera skyward.

---

### Task 2 — Custom LookAt

`glm.lookAt()` hides the matrix construction. Implement the stub:

```python
def custom_look_at(pos, target, world_up):
    ...
```

without calling `glm.lookAt()`, then replace the `glm.lookAt()` call in `render()` with `custom_look_at(...)`.

**Steps:**

1. Compute forward `f = normalize(target - pos)`
2. Compute right `r = normalize(cross(f, world_up))`
3. Compute true up `u = cross(r, f)`
4. Build the 4×4 view matrix:

```
| r.x   r.y   r.z   -dot(r, pos) |
| u.x   u.y   u.z   -dot(u, pos) |
| -f.x  -f.y  -f.z   dot(f, pos) |
| 0     0     0      1           |
```

Note: pyglm matrices are column-major — `m[col][row]`.

**Expected result:** visually identical to lesson 025 because `custom_look_at` produces the same matrix as `glm.lookAt`.

## Files

| File | Description |
|------|-------------|
| `exercise_camera.py` | Starter code with `# TODO` markers |
| `shaders/cube.vert` | MVP transform (unchanged from 025) |
| `shaders/cube.frag` | Texture sample (unchanged from 025) |

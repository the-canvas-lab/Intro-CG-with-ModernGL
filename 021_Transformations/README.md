# Transformations

Moving, rotating, and scaling geometry in code means multiplying every vertex by a **transformation matrix**. A single 4×4 matrix can encode all three operations at once, and the vertex shader applies it to every vertex in one GPU operation.

## Why 4×4 and not 3×3?

Translation cannot be expressed as a 3×3 matrix multiplication — you would need an addition. By moving to **homogeneous coordinates** (adding a fourth component w=1 to positions), translation becomes a multiplication too, and all three transforms unify into one matrix type.

## The Three Transforms

**Scale** — stretches or shrinks along each axis:

```
| Sx  0   0   0 |
|  0  Sy  0   0 |
|  0   0  Sz  0 |
|  0   0   0  1 |
```

**Translation** — shifts by (Tx, Ty, Tz):

```
| 1   0   0   Tx |
| 0   1   0   Ty |
| 0   0   1   Tz |
| 0   0   0    1 |
```

**Rotation** around the Z axis by angle θ:

```
| cos θ  -sin θ   0   0 |
| sin θ   cos θ   0   0 |
|   0       0     1   0 |
|   0       0     0   1 |
```

## Combining Transforms with pyglm

`pyglm` mirrors the C++ GLM API. Each function appends the new operation **on the right** of the current matrix:

```python
import glm

transform = glm.mat4(1.0)                                      # identity
transform = glm.translate(transform, glm.vec3(0.5, -0.5, 0.0)) # T * I  = T
transform = glm.rotate(transform, time, glm.vec3(0, 0, 1))     # T * R
transform = glm.scale(transform, glm.vec3(0.5, 0.5, 0.5))      # T * R * S
```

The final matrix is **T × R × S**. The GPU computes `(T × R × S) × vertex`, which processes right-to-left:

1. **S** scales the vertex
2. **R** rotates it
3. **T** translates it

**The code is written top-to-bottom in the opposite order of how it affects geometry.** Reading the three lines bottom-to-top tells you what happens to the mesh.

## Passing a mat4 to the Shader

```glsl
// vertex shader
uniform mat4 u_transform;

void main() {
    gl_Position = u_transform * vec4(in_position, 1.0);
}
```

```python
# Python — pyglm mat4 supports the buffer protocol
self.program['u_transform'].write(transform)
```

## This Program

A textured quad is scaled to 50%, then rotated continuously around the Z axis, then moved to the bottom-right corner `(0.5, -0.5)`. The result is a quad that spins in place at an offset position.

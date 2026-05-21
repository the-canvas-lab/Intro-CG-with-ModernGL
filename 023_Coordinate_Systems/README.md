# Coordinate Systems

Every 3D rendering pipeline moves vertex positions through a sequence of **coordinate spaces**, each defined by its own origin and axes. Keeping them separate makes the math composable: objects are built in their own space, placed in the world, viewed through a camera, and finally projected onto the screen.

## The Five Spaces

```
local space  →[model]→  world space  →[view]→  view space  →[projection]→  clip space  →[viewport]→  screen space
```

| Space | Also called | What it means |
|---|---|---|
| Local | Object space | Coordinates as defined in the 3D modelling tool, relative to the object's own origin |
| World | — | Coordinates after the object is placed in the scene |
| View | Camera / Eye space | Coordinates relative to the camera — camera is at origin, looking toward −Z |
| Clip | — | Coordinates after the projection divide; outside [−1, 1] on any axis are clipped |
| Screen | NDC | Final pixel coordinates after the viewport transform |

## The Three Matrices

```glsl
gl_Position = u_projection * u_view * u_model * vec4(in_position, 1.0);
```

**Model matrix** — places the object in the world (translate, rotate, scale). Every object has its own model matrix; it is the only one that changes per object in a multi-object scene.

**View matrix** — moves everything relative to the camera. Moving the camera back by 3 units is identical to moving the whole scene forward by 3 units:

```python
view = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 0.0, -3.0))
```

**Projection matrix** — transforms view space into clip space and encodes the perspective effect (distant objects appear smaller). `glm.perspective` builds a **frustum**: a truncated pyramid. Only geometry inside the frustum survives clipping.

```python
# fov    : vertical field of view (radians)
# aspect : width / height — must match the window to avoid distortion
# near   : closest visible distance (must be > 0)
# far    : farthest visible distance
projection = glm.perspective(glm.radians(45.0), 800 / 600, 0.1, 100.0)
```

## Depth Testing

Without a depth test the GPU writes each fragment over whatever was drawn before, regardless of distance. Enabling depth testing makes it compare the incoming fragment's depth against the stored value and discard anything farther away:

```python
self.ctx.enable(self.ctx.DEPTH_TEST)
```

`ctx.clear()` resets the depth buffer to 1.0 (maximum distance) at the start of every frame so each frame starts clean.

## This Program

A textured cube rotates continuously around a tilted axis. The projection matrix is computed once in `__init__` since the window size and FOV are fixed; the model matrix is rebuilt every frame to drive the animation.

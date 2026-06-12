# Lesson 041 — Face Culling

## Run

```
python 041_Face_Culling/face_culling.py
```

## Controls

| Key | Action |
|-----|--------|
| ← / → | Switch culling mode |
| Esc | Quit |

## Core Concept

### Winding order decides front vs. back

A triangle's *front* is the side from which its vertices appear in
counter-clockwise order (the OpenGL default; configurable via
`ctx.front_face`). Closed objects are modelled so that all triangles face
**outward** — which means the camera can never see a back face: each one is
hidden behind the object's own front faces.

### Culling: discard them early

```python
ctx.enable(moderngl.CULL_FACE)
ctx.cull_face = 'back'
```

With culling on, the GPU drops back-facing triangles *before* rasterization.
On a closed mesh nothing changes visually — the depth test was already
hiding those faces — but roughly **half of all triangles** skip
rasterization and fragment shading entirely. That is why back-face culling
is enabled in essentially every real renderer.

### Why this demo uses an open box

Because on a closed cube all the modes look the same! The demo box is
missing its front wall, so the camera can see inside as it spins. The
fragment shader detects back faces with `gl_FrontFacing` and colours each
interior wall a slightly different blue — a per-face ID vertex attribute
indexes a small tint table, shaded top-bright/bottom-dark so the inside
reads as a room with five distinguishable walls:

| Mode | What you see |
|------|--------------|
| 1 — No culling | The blue interior walls through the opening |
| 2 — Cull back | The interior vanishes: when the opening faces you, you see **straight through** the box to the background |
| 3 — Cull front | The textured exterior vanishes; only the blue interior renders — the box turns inside out |

Mode 2 is the famous "see-through walls" artifact from games: clip the
camera inside any wall and the world appears through it, because you are
looking at the culled side of one-sided geometry.

### The #1 winding bug

If a model shows holes the moment culling is enabled, some of its triangles
are wound the wrong way (or the file uses CW-front like some exporters do).
Try it: swap any two vertices of one triangle in `BOX_VERTS` and that wall
will disappear in mode 2 — exactly the bug you will some day meet in the
wild. Note `mat4` transforms can flip winding too: a negative scale (mirror)
turns every CCW triangle CW.

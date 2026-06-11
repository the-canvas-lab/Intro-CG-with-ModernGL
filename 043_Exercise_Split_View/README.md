# Exercise 043 — Split-View Post-Processing

## Run

```
python 043_Exercise_Split_View/exercise_split_view.py
```

## Controls

| Key | Action |
|-----|--------|
| Esc | Quit |

## Goal

Implement a split-screen viewer that renders the same FBO texture twice — the left half showing the original scene, the right half showing a grayscale conversion. This requires wiring up the two-pass framebuffer pipeline yourself and writing the effect shader.

## TODOs

### TODO 1 — Create the offscreen FBO (`exercise_split_view.py`)

The scene must be rendered into a texture rather than directly to the window. You need:

1. **Colour texture** — the render target the GPU writes colour data into:
   ```python
   self.color_tex = self.ctx.texture((W, H), 4)
   self.color_tex.filter = moderngl.LINEAR, moderngl.LINEAR
   ```

2. **Depth renderbuffer** — required for the depth test during Pass 1, but never sampled:
   ```python
   depth_buf = self.ctx.depth_renderbuffer((W, H))
   ```

3. **Framebuffer object** — attaches both to create the offscreen render target:
   ```python
   self.fbo = self.ctx.framebuffer(
       color_attachments=[self.color_tex],
       depth_attachment=depth_buf,
   )
   ```

4. **Bind the colour texture** to unit 1 so it doesn't clash with the scene texture already on unit 0:
   ```python
   self.color_tex.use(location=1)
   ```

### TODO 2 — Build the screen-quad programs and VAOs (`exercise_split_view.py`)

Pass 2 draws two half-screen quads. The vertex data (`LEFT_QUAD`, `RIGHT_QUAD`) is already defined — each stores `(ndc_x, ndc_y, uv_x, uv_y)` per vertex, with NDC x covering its respective half and UV x covering the full 0→1 range so both halves show the complete scene.

For each half you need a shader program, a VBO, and a VAO:

```python
# Left — passthrough
self.passthrough_prog = self.ctx.program(
    vertex_shader=load_shader('shaders/screen.vert'),
    fragment_shader=load_shader('shaders/passthrough.frag'),
)
self.passthrough_prog['u_screen'] = 1
left_vbo = self.ctx.buffer(LEFT_QUAD.tobytes())
self.left_vao = self.ctx.vertex_array(
    self.passthrough_prog,
    [(left_vbo, '2f 2f', 'in_position', 'in_uv')],
)

# Right — your effect (same pattern, use RIGHT_QUAD and effect.frag)
```

### TODO 3 — Grayscale effect (`shaders/effect.frag`)

The texture colour is already sampled into `col`. Convert it to grayscale using a weighted dot product. Human eyes are more sensitive to green than red, and least sensitive to blue — the ITU-R BT.601 standard encodes this as:

```
grey = 0.2126 * R + 0.7152 * G + 0.0722 * B
```

In GLSL, `dot()` computes exactly this:

```glsl
float grey = dot(col, vec3(0.2126, 0.7152, 0.0722));
out_color = vec4(vec3(grey), 1.0);
```

## Why two separate quads?

Both quads sample the same FBO texture at the same UV coordinates, so they see the exact same scene image. The only difference is which fragment shader is applied. Using two distinct programs — one per half — keeps the effects completely independent and makes the before/after comparison immediate.

The alternative (one full-screen quad, branch on `gl_FragCoord.x`) would also work but conflates geometry and effect logic in a single shader, which is harder to extend.

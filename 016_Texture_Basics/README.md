# Texture Basics

So far, fragment color has come from vertex attributes or uniforms. **Textures** let the fragment shader sample color from an image stored on the GPU, giving geometry rich surface detail without packing all that data into the vertex buffer.

## UV Coordinates

Every vertex carries a pair of texture coordinates called **UVs** (u, v). UV (0, 0) maps to the bottom-left corner of the image; (1, 1) maps to the top-right. The GPU interpolates UVs across the triangle surface (the same fragment interpolation from lesson 010), so each fragment receives the UV for its exact screen position and samples the image at that point.

```glsl
in vec2 in_uv;
out vec2 uv;

void main() {
    gl_Position = vec4(in_position, 1.0);
    uv = in_uv;
}
```

## Loading a Texture

On the CPU, the image is loaded with pygame and uploaded to the GPU as a moderngl `Texture`:

```python
image = pygame.image.load(path).convert_alpha()
image = pygame.transform.flip(image, False, True)   # flip vertically
data  = pygame.image.tostring(image, 'RGBA')
texture = ctx.texture(image.get_size(), 4, data)
```

The vertical flip is necessary because OpenGL's texture origin is at the **bottom-left**, while pygame (and most image formats) store pixels from the **top-left** down.

## Texture Units and Samplers

The GPU has a fixed number of **texture units** (at least 16). A texture must be *bound* to a unit before a draw call, and the fragment shader references that unit through a `sampler2D` uniform set to the same unit number:

```python
texture.use(location=0)       # bind to unit 0
program['u_texture'] = 0      # tell the shader to sample from unit 0
```

```glsl
uniform sampler2D u_texture;

void main() {
    out_color = texture(u_texture, uv);
}
```

## This Program

A rectangle is drawn with UVs covering the full image (0 to 1 on both axes). The fragment shader samples `container.jpg` at each interpolated UV, mapping the image onto the quad.

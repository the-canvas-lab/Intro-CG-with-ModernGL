# Texture Filtering

When a texture is displayed at a size different from its original resolution, the GPU must decide how to map texels to screen pixels. The rule it uses is called the **filter mode**.

## NEAREST vs LINEAR

| Mode | Behavior | Result |
|------|----------|--------|
| `GL_NEAREST` | Pick the single closest texel | Sharp, blocky pixels |
| `GL_LINEAR` | Blend the four surrounding texels (bilinear) | Smooth, blurred edges |

The filter is set separately for two situations:

- **Magnification** — texture is stretched (zoomed in). This is what this program demonstrates.
- **Minification** — texture is shrunk (zoomed out). Mipmaps are usually involved here.

```python
texture.filter = (min_filter, mag_filter)
```

## Mipmaps

Mipmaps are a pre-generated chain of half-size copies of the texture (full → ½ → ¼ → …). The GPU automatically picks the mip level closest in size to the area being drawn, avoiding aliasing on distant or small objects.

Mipmap filter modes such as `LINEAR_MIPMAP_LINEAR` only apply to the **minification** filter — magnification never uses mipmaps. In moderngl, calling `build_mipmaps()` internally overrides the filter to `LINEAR_MIPMAP_LINEAR`, so it is intentionally omitted in this program where we want explicit control over the magnification filter.

## This Program

The same `europeMap.png` is loaded twice — once with `NEAREST` and once with `LINEAR`. UVs sample a 10% region centered on the texture (~10× magnification), making individual texels large enough to see the difference clearly. The left rectangle shows the blocky NEAREST result; the right shows the smooth LINEAR result.

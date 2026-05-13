# Shader Files

In program 001 the GLSL source was written as inline Python strings. This works, but it loses syntax highlighting, makes the Python file harder to read, and mixes two different languages in one file.

## Separating Shaders

Moving each shader into its own file (`.vert` for vertex, `.frag` for fragment) solves all three problems. The `load_shader()` helper reads the file at runtime and passes the source string to `ctx.program()` — exactly as before, just loaded from disk instead of written inline.

```python
def load_shader(path):
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, path)) as f:
        return f.read()
```

The path is resolved relative to the script's own directory (`__file__`), not the working directory. This means the program runs correctly regardless of where you launch it from.

## This Program

Identical behaviour to 001 — the same triangle, the same color. The only change is where the shader source lives.

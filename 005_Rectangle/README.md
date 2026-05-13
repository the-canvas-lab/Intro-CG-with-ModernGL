# Drawing a Rectangle

OpenGL only draws triangles as its basic filled primitive. To draw a rectangle, you decompose it into two triangles that share a diagonal edge.

## Six Vertices, Two Triangles

```
3 ──────── 0
│        ╱ │
│      ╱   │
│    ╱     │
│  ╱       │
2 ──────── 1
```

Triangle 1: vertices 0, 1, 3 (top right, bottom right, top left)  
Triangle 2: vertices 1, 2, 3 (bottom right, bottom left, top left)

The diagonal vertices — bottom right (1) and top left (3) — appear in both triangles, so they must be listed twice in the buffer. This duplication is harmless for six vertices, but becomes wasteful as geometry grows larger.

## This Program

The six vertices are stored in a flat array and rendered with a single draw call. Program 006 eliminates the duplication using an index buffer.

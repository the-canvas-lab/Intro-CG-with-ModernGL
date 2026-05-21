# Exercise: Atlas UV Mapping

In tools like Blender, **UV unwrapping** is the process of assigning each face of a mesh to a region of a texture. The UV editor shows the mesh "unfolded" into 2D, and you drag the UV islands to align them with the parts of the texture you want to use. This exercise is the same operation, stripped down to its essentials: six quads, one atlas, and UV coordinates to fill in.

## The Atlas

`numbers.png` is a 3-column × 2-row texture atlas. As it appears in the image file:

```
+----------+----------+----------+
|    1     |    2     |    3     |  ← row 0 (top of image)
+----------+----------+----------+
|    4     |    5     |    6     |  ← row 1 (bottom of image)
+----------+----------+----------+
```

After the vertical flip applied on load (correcting OpenGL's bottom-left origin), the UV layout is:

```
v = 1.0  ┌──────────┬──────────┬──────────┐
          │    1     │    2     │    3     │
v = 0.5  ├──────────┼──────────┼──────────┤
          │    4     │    5     │    6     │
v = 0.0  └──────────┴──────────┴──────────┘
        u = 0.0   1/3       2/3       1.0
```

## What to do

Open `exercise_atlas_uv.py`. Six quads are already placed on screen in a matching 3×2 grid. Each quad has placeholder UV values `(0.0, 0.0, 0.0, 0.0)` — your task is to replace them with the correct `u0, u1, v0, v1` values so each quad displays the number that belongs in that position.

## Tasks

For each quad, compute:
- `u0 = col / 3.0`  — left edge of the atlas cell
- `u1 = (col + 1) / 3.0`  — right edge
- `v0`, `v1`  — vertical range, keeping in mind the Y-flip

## The Y-flip gotcha

This is the same confusion you encounter in Blender when a UV map appears upside-down. The image file stores row 0 at the top, but OpenGL's v=0 is at the bottom. After the vertical flip, image row 0 (numbers 1–3) ends up at the **top** of UV space (`v: 0.5 → 1.0`), not the bottom.

Getting this wrong is part of the exercise — if your numbers appear in the wrong row, flip your v0 and v1 values.

## Self-verification

- All six numbers visible, no number repeated
- Top row shows 1, 2, 3 (left to right)
- Bottom row shows 4, 5, 6 (left to right)
- If rows are swapped → v ranges for rows 0 and 1 are reversed
- If columns are swapped → u ranges are wrong

## Concepts reviewed

- Texture atlas structure and UV cell boundaries
- How UV coordinates select a sub-region of a texture
- The image Y-flip and its effect on v coordinates

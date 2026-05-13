# Exercise: Position as Color

This exercise builds directly on the fragment interpolation concept introduced in `010_Stride_Offset/README.md`.

## What to do

Open `exercise_position_color.py` and follow the TODO comments. Pass `in_position` directly to the fragment shader as a color — no remapping.

## What to observe

After it works, look at the result and answer these questions:

- Parts of the triangle are black even though no vertex was colored black. Why?
- Which screen axis controls the red channel? Which controls green?
- The blue channel looks flat and dim. Why?

## Concepts reviewed

- Passing data between shader stages with `out` / `in` variables
- Fragment interpolation — the GPU blends `v_color` across the triangle automatically
- Color channel clamping — negative position values map to zero (black)

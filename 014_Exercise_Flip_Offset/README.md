# Exercise: Flip and Offset

This exercise applies uniforms (013) to position rather than color.

## What to do

Open `exercise_flip_offset.py`. The Python side is already complete — it animates `u_offset` automatically. Only the vertex shader needs to be modified.

## Tasks

1. Negate the y component of `in_position` to flip the triangle upside down.
2. Add `u_offset` to the x and y components to make the triangle move.

## Self-verification

- If the flip is missing → triangle points upward instead of downward
- If the offset is missing → triangle stays centered and does not oscillate
- Both correct → upside-down triangle oscillating left and right

## Concepts reviewed

- Modifying `gl_Position` in the vertex shader
- Applying a `vec2` uniform to position

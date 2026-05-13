# Exercise: Pulsing Rectangle (Capstone)

This is a cumulative exercise combining every major concept from programs 006–013.

## What to do

Open `exercise_pulsing_rectangle.py` and follow the numbered TODO comments. Also complete the two shader files.

## Expected result

A rectangle where the two vertices on the shared diagonal are red and pulse in brightness over time, while the other two corners remain black at all times.

## Concepts reviewed

| Concept | Program |
|---------|---------|
| Index buffer | 006 |
| Interleaved vertex data (position + color) | 010 |
| Passing color between shader stages | 010 |
| Time uniform | 013 |
| Brightness modulation via `sin()` | 013 |

## Key insight

Black vertices `(0, 0, 0)` multiplied by any brightness value always remain `(0, 0, 0)`. If the black corners start glowing, the brightness is being applied before the color is read — check the order of operations in the vertex shader.

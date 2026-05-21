# Exercise: Dynamic Blend

This exercise extends lesson 017 (Multiple Textures) by making the blend ratio controllable at runtime via a uniform and keyboard input.

## What to do

Open `exercise_dynamic_blend.py` and `shaders/rect.frag`. Both need changes.

## Tasks

1. In `shaders/rect.frag`, add a `uniform float u_mix` and replace the hardcoded `0.2` in `mix()` with `u_mix`.

2. In `Scene.__init__`, add `self.mix_amount = 0.2` to track the current blend ratio.

3. In `Scene.render`, upload the value each frame:
   ```python
   self.program['u_mix'] = self.mix_amount
   ```

4. In the event loop, handle `pygame.KEYDOWN`:
   - `pygame.K_UP` → increase `self.mix_amount` by `0.05`
   - `pygame.K_DOWN` → decrease `self.mix_amount` by `0.05`
   - Clamp to `[0.0, 1.0]` so the value never goes out of range.

## Self-verification

- Press UP repeatedly → the face texture gradually takes over
- Press DOWN repeatedly → the container texture gradually takes over
- Holding at 0.0 → only the container visible
- Holding at 1.0 → only the face visible

## Concepts reviewed

- Passing a runtime value from CPU to GPU via a uniform
- Updating state from keyboard events inside the pygame event loop
- `mix()` with a dynamic parameter

# Fragment Interpolation

Run this program and notice that the triangle shows a smooth color gradient even though only three colors were specified — one per vertex. This is **fragment interpolation**.

## What is a fragment?

A fragment is roughly one pixel on the screen covered by a triangle. For a triangle that covers hundreds of pixels, the GPU runs the fragment shader hundreds of times — once per fragment.

## How interpolation works

After the vertex shader runs for each of the three vertices, the GPU rasterizes the triangle: it determines which pixels it covers and, for each one, computes an interpolated value for every `out` variable declared in the vertex shader.

The interpolation is based on how close the fragment is to each vertex. A fragment sitting exactly on the red vertex receives `v_color = (1, 0, 0)`. A fragment at the center of the triangle receives an equal blend of all three vertex colors. This blending is done automatically — the fragment shader just receives the already-interpolated `v_color` and uses it.

## Why it matters

Fragment interpolation is not limited to colors. Any value passed from the vertex shader to the fragment shader — texture coordinates, normals, positions — is interpolated the same way. This is the mechanism that makes smooth shading, texture mapping, and lighting all work.

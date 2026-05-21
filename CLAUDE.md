# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A step-by-step computer graphics tutorial series using **moderngl** + **pygame**, following [learnopengl.com](https://learnopengl.com) content adapted for Python. Each lesson lives in its own numbered folder (e.g., `001_Hello_Triangle/`).

## Environment

- Python via Conda (managed by VS Code ms-python.python extension)
- Key dependencies: `moderngl`, `pygame`, `pyglm`

## Running a Lesson

```bash
python 001_Hello_Triangle/hello_triangle.py
```

Run each lesson's script directly — no build step required. Window is 800×600, DPI-aware, with vsync.

## Program List

| # | Folder | Concept |
|---|--------|---------|
| 001 | `001_Hello_Triangle` | Inline shaders, hardcoded vertices inside the vertex shader |
| 002 | `002_Shader_Files` | Loading shaders from separate `.vert` / `.frag` files |
| 003 | `003_Vertex_Buffer` | Uploading vertex data from CPU to GPU via a VBO |
| 004 | `004_Exercise_Two_Triangles` | **Exercise**: two triangles side by side in a single draw call |
| 005 | `005_Rectangle` | Rectangle from 6 vertices (two triangles, duplicated corners) |
| 006 | `006_Index_Buffer` | Index buffer (IBO) to eliminate duplicate vertices |
| 007 | `007_Multiple_Objects` | Two independent VAO/VBO pairs for separate objects |
| 008 | `008_Multiple_Shaders` | Two shader programs to render objects in different colors |
| 009 | `009_Exercise_Rectangle_Triangle` | **Exercise**: rectangle + triangle with separate shaders and index buffer |
| 010 | `010_Stride_Offset` | Interleaved position + color in one buffer; stride and byte offset |
| 011 | `011_Exercise_Position_Color` | **Exercise**: output vertex position directly as fragment color; observe clamping of negative values |
| 012 | `012_GLSL_Vectors` | GLSL vector types, component access (.x/.y/.z/.w), swizzling, color derived from position |
| 013 | `013_Uniforms` | Uniforms — CPU-set values constant across a draw call; animated color via `u_time` |
| 014 | `014_Exercise_Flip_Offset` | **Exercise**: flip triangle vertically and translate with animated vec2 uniform |
| 015 | `015_Exercise_Pulsing_Rectangle` | **Exercise**: rectangle via index buffer, red diagonal pulses via u_time, black corners stay dark |
| 016 | `016_Texture_Basics` | Loading an image with pygame, uploading as a ModernGL texture, UV coordinates, sampling in the fragment shader |
| 017 | `017_Multiple_Textures` | Two textures bound to separate units, both sampled in the fragment shader and blended with `mix()` |
| 018 | `018_Texture_Filtering` | One texture rendered on two side-by-side quads: left with NEAREST, right with LINEAR; UVs magnified 5× to make the difference visible |
| 019 | `019_Exercise_Dynamic_Blend` | **Exercise**: add `u_mix` uniform to the shader and use UP/DOWN arrow keys to control the blend ratio at runtime |
| 020 | `020_Exercise_Atlas_UV` | **Exercise**: assign UV coordinates to 6 quads to map each cell of a 3×2 texture atlas; introduces the UV Y-flip gotcha |
| 021 | `021_Transformations` | 4×4 transformation matrices (scale, rotate, translate) via pyglm; `mat4` uniform in vertex shader; right-to-left application order |
| 022 | `022_Exercise_Transform_Order` | **Exercise**: swap rotate/translate order to observe spinning-in-place vs orbiting; add a second quad with sin() pulsing scale |
| 023 | `023_Coordinate_Systems` | The 5 coordinate spaces (local → world → view → clip → screen); model/view/projection matrices; depth testing; textured rotating cube |
| 024 | `024_Exercise_Multiple_Model_Matrices` | **Exercise**: render 10 cubes at different positions with unique tilts; animate every third cube by chaining a time-based rotation |
| 025 | `025_Camera` | Free-fly camera: glm.lookAt() built from camera_pos/front/up vectors; WASD movement scaled by delta_time; mouse look via Euler angles (yaw/pitch); scroll zoom via FOV |
| 026 | `026_Exercise_Camera` | **Exercise**: (1) FPS-style movement locked to the XZ plane; (2) implement custom_look_at() manually from camera basis vectors |

## Code Conventions

Each lesson follows this pattern:

- **Window**: created via `pygame` with `pygame.OPENGL | pygame.DOUBLEBUF` flags; `SDL_WINDOWS_DPI_AWARENESS=permonitorv2` set before init
- **Context**: obtained via `moderngl.get_context()` (pygame creates the GL context, moderngl wraps it)
- **Scene class**: encapsulates shader program, VAO, and per-frame `render()` logic
- **Shaders**: from 002 onwards, loaded from separate `.vert` / `.frag` files via a `load_shader()` helper that resolves paths relative to the script
- **Main loop**: `pygame` event loop calling `scene.render()` then `pygame.display.flip()`

## Adding a New Lesson

1. Create a new folder with the next number and topic name (e.g., `011_Textures/`)
2. Copy `load_shader()` and the pygame init block from the previous lesson as a starting point
3. Exercises are prefixed with `exercise_` in the filename and contain `# TODO` markers for students

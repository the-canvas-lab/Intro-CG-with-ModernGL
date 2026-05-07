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

## Code Conventions

Each lesson follows this pattern:

- **Window**: created via `pygame` with `pygame.OPENGL | pygame.DOUBLEBUF` flags; `SDL_WINDOWS_DPI_AWARENESS=permonitorv2` set before init
- **Context**: obtained via `moderngl.get_context()` (pygame creates the GL context, moderngl wraps it)
- **Scene class**: encapsulates shader program, VAO, and per-frame `render()` logic
- **Shaders**: written inline as GLSL strings (`#version 330 core`); loaded into `ctx.program(vertex_shader=..., fragment_shader=...)`
- **Main loop**: `pygame` event loop calling `scene.render()` then `pygame.display.flip()`

## Adding a New Lesson

1. Create a new folder with the next number and topic name (e.g., `002_Shaders/`)
2. Copy the structure from the previous lesson as a starting point
3. Keep shaders inline unless they grow large enough to warrant separate `.glsl` files

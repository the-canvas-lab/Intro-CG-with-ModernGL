# Introduction to Computer Graphics

A step-by-step computer graphics tutorial series using **moderngl** and **pygame**, following [learnopengl.com](https://learnopengl.com) content adapted for Python.

Each lesson lives in its own numbered folder and can be run independently.

---

## Setup

### Prerequisites

- [Anaconda](https://www.anaconda.com/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- VS Code with the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

### Create the environment

```bash
conda env create -f environment.yml
conda activate CG
```

### Select the interpreter in VS Code

Open the Command Palette (`Ctrl+Shift+P`) → **Python: Select Interpreter** → choose the `CG` conda environment.

---

## Running a Lesson

```bash
python 001_Hello_Triangle/hello_triangle.py
```

Run each lesson's script directly from the project root. No build step is required. The window opens at 800×600 with vsync enabled. Close it with the window's X button.

---

## Lessons

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
| 012 | `012_GLSL_Vectors` | GLSL vector types, component access (`.x/.y/.z/.w`), swizzling, color derived from position |
| 013 | `013_Uniforms` | Uniforms — CPU-set values constant across a draw call; animated color via `u_time` |
| 014 | `014_Exercise_Flip_Offset` | **Exercise**: flip triangle vertically and translate with animated `vec2` uniform |
| 015 | `015_Exercise_Pulsing_Rectangle` | **Exercise**: rectangle via index buffer, red diagonal pulses via `u_time`, black corners stay dark |
| 016 | `016_Texture_Basics` | Loading an image with pygame, uploading as a ModernGL texture, UV coordinates, sampling in the fragment shader |
| 017 | `017_Exercise_Texture_Wrapping` | **Exercise**: UVs span 0–2; toggle `WRAP_REPEAT` between `True` (GL_REPEAT) and `False` (GL_CLAMP_TO_EDGE) |
| 018 | `018_Texture_Filtering` | NEAREST vs LINEAR filtering shown side-by-side on a magnified texture region; mipmap concepts explained in comments |
| 019 | `019_Multiple_Textures` | Two textures bound to separate units, both sampled in the fragment shader and blended with `mix()` |
| 020 | `020_Exercise_Dynamic_Blend` | **Exercise**: add `u_mix` uniform to the shader and use UP/DOWN arrow keys to control the blend ratio at runtime |
| 028 | `028_Colors` | Color as component-wise multiplication of light and object color; two-cube scene (lit object + orbiting lamp) |
| 029 | `029_Basic_Lighting` | Phong lighting model: ambient + diffuse + specular; normal vectors in VBO; normal matrix |
| 030 | `030_Exercise_Gouraud` | **Exercise**: move Phong calculations to the vertex shader; observe banding artifacts from per-vertex interpolation |
| 031 | `031_Materials` | Material struct (ambient/diffuse/specular/shininess) + Light struct; real-world material presets |
| 032 | `032_Exercise_Dynamic_Light` | **Exercise**: animate light color via `sin(time)`; update lamp cube color to match |

Exercise folders contain `# TODO` markers where you fill in the implementation.

---

## Project Structure

```
IntroCG/
├── 001_Hello_Triangle/
│   └── hello_triangle.py
├── 002_Shader_Files/
│   ├── shader_files.py
│   ├── shader.vert
│   └── shader.frag
│   ...
└── README.md
```

From lesson 002 onwards, each folder contains a Python script plus `.vert` and `.frag` shader files loaded at runtime.

---

## Code Structure

Every lesson follows the same pattern:

- **pygame** creates an OpenGL window (`pygame.OPENGL | pygame.DOUBLEBUF`, vsync on, DPI-aware)
- **moderngl** wraps the existing GL context via `moderngl.get_context()`
- A `Scene` class holds the shader program, VAO, and a `render()` method called once per frame
- Shaders (from lesson 002 onwards) are loaded from separate files via a `load_shader()` helper

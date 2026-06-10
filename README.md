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

Run each lesson's script directly from the project root. No build step is required. The window opens at 800×600 with vsync enabled.

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
| 017 | `017_Multiple_Textures` | Two textures bound to separate units, both sampled in the fragment shader and blended with `mix()` |
| 018 | `018_Texture_Filtering` | One texture rendered on two side-by-side quads: left with NEAREST, right with LINEAR; UVs magnified 5× to make the difference visible |
| 019 | `019_Exercise_Dynamic_Blend` | **Exercise**: add `u_mix` uniform to the shader and use UP/DOWN arrow keys to control the blend ratio at runtime |
| 020 | `020_Exercise_Atlas_UV` | **Exercise**: assign UV coordinates to 6 quads to map each cell of a 3×2 texture atlas; introduces the UV Y-flip gotcha |
| 021 | `021_Transformations` | 4×4 transformation matrices (scale, rotate, translate) via pyglm; `mat4` uniform in vertex shader; right-to-left application order |
| 022 | `022_Exercise_Transform_Order` | **Exercise**: swap rotate/translate order to observe spinning-in-place vs orbiting; add a second quad with sin() pulsing scale |
| 023 | `023_Coordinate_Systems` | The 5 coordinate spaces (local → world → view → clip → screen); model/view/projection matrices; depth testing; textured rotating cube |
| 024 | `024_Exercise_Multiple_Model_Matrices` | **Exercise**: render 10 cubes at different positions with unique tilts; animate every third cube by chaining a time-based rotation |
| 025 | `025_Camera` | Free-fly camera: `glm.lookAt()` built from camera_pos/front/up vectors; WASD movement scaled by delta_time; mouse look via Euler angles (yaw/pitch); scroll zoom via FOV |
| 026 | `026_Exercise_Camera` | **Exercise**: (1) FPS-style movement locked to the XZ plane; (2) implement `custom_look_at()` manually from camera basis vectors |
| 027 | `027_Model_Loading` | Load geometry from a `.obj` file via pywavefront; OBJ format (v/vt/vn/f); T2F_N3F_V3F interleaved layout; replaces hard-coded vertex arrays |
| 028 | `028_Colors` | Color as component-wise multiplication of light and object color; two-cube scene (lit object + orbiting lamp); two VAOs, two shader programs |
| 029 | `029_Basic_Lighting` | Phong lighting model: ambient + diffuse + specular; normal vectors in VBO; normal matrix for correct shading under non-uniform scale |
| 030 | `030_Phong_Components` | Phong component decomposition: `uniform int u_mode` isolates ambient / diffuse / specular / full; ← → to switch; orbiting lamp shows each component's behaviour |
| 031 | `031_Exercise_Gouraud` | **Exercise**: split-screen Phong (left, reference) vs Gouraud (right, TODO); move Phong to vertex shader and observe interpolation banding side by side |
| 032 | `032_Materials` | Material struct (ambient/diffuse/specular/shininess) + Light struct; real-world material presets from the devernay table |
| 033 | `033_Material_Selector` | GLSL uniform arrays (`uniform Material materials[8]`); upload all presets at startup; switch active material at runtime via `uniform int u_material_index`; ← → keys |
| 034 | `034_Lighting_Maps` | Replace uniform material colors with textures; `sampler2D diffuse` and `sampler2D specular` in Material struct; UV coordinates added to VBO; per-fragment highlight intensity from specular map |
| 035 | `035_Exercise_Emission_Map` | **Exercise**: add `sampler2D emission` to Material struct; sample `container2_emission.png` and add to final color — glow is independent of the lamp |
| 036 | `036_Light_Casters` | Directional / Point / Spot in one scene; ← → to switch; fixed light position so comparisons are isolated — same angle shows attenuation (→ Point) then cone restriction (→ Spot) |
| 037 | `037_Exercise_Flashlight` | **Exercise**: attach spot light to camera — set `light.position = camera_pos` and `light.direction = camera_front` each frame; ambient = 0 for dramatic effect |

Exercise folders contain `# TODO` markers where you fill in the implementation.

---

## Project Structure

```
Intro-CG-with-ModernGL/
├── 001_Hello_Triangle/
│   └── hello_triangle.py
├── 002_Shader_Files/
│   ├── shader_files.py
│   ├── shader.vert
│   └── shader.frag
├── ...
├── images/          # shared textures
├── models/          # shared .obj files
└── README.md
```

From lesson 002 onwards, each folder contains a Python script plus `.vert` and `.frag` shader files loaded at runtime. Lessons 016+ also reference shared assets in `images/` and `models/`.

---

## Code Structure

Every lesson follows the same pattern:

- **pygame** creates an OpenGL window (`pygame.OPENGL | pygame.DOUBLEBUF`, vsync on, DPI-aware)
- **moderngl** wraps the existing GL context via `moderngl.get_context()`
- A `Scene` class holds the shader program, VAO, and a `render()` method called once per frame
- Shaders (from lesson 002 onwards) are loaded from separate files via a `load_shader()` helper

#version 330 core

layout (location = 0) out vec4 out_color;

// TODO: Declare an input variable 'v_color' of type vec3 to receive the
//       interpolated color from the vertex shader.

void main() {
    // TODO: Replace the hardcoded color with 'v_color'.
    //       Use 1.0 as the alpha component.
    out_color = vec4(1.0, 0.5, 0.2, 1.0);
}

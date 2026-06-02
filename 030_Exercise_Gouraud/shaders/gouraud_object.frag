#version 330 core

layout (location = 0) out vec4 out_color;

// TODO: Declare the matching "in vec3" to receive gouraud_color from the vertex shader.

void main() {
    // TODO: Output your received colour as vec4(..., 1.0).
    out_color = vec4(1.0, 0.0, 1.0, 1.0);  // magenta placeholder — replace this
}

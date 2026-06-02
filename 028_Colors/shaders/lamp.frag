#version 330 core

layout (location = 0) out vec4 out_color;

void main() {
    // The lamp cube always renders white regardless of lighting calculations —
    // it represents the light source itself, not a lit object.
    out_color = vec4(1.0);
}

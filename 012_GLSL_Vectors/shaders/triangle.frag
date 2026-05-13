#version 330 core

layout (location = 0) out vec4 out_color;

in vec3 v_color;

void main() {
    // Construct a vec4 from a vec3 + a float — a common swizzle pattern.
    out_color = vec4(v_color, 1.0);
}

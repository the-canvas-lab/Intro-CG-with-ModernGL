#version 330 core

in vec2 in_position;
in vec2 in_offset;   // per-instance: NDC position of this quad's centre
in vec3 in_color;    // per-instance: RGB color

out vec3 color;

void main() {
    color       = in_color;
    // Scale the unit quad down to 0.08 units, then shift to its instance slot.
    gl_Position = vec4(in_position * 0.08 + in_offset, 0.0, 1.0);
}

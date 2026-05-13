#version 330 core

layout (location = 0) out vec4 out_color;

// A uniform is a value sent from the CPU that stays constant for every
// fragment processed in a single draw call. Unlike vertex attributes,
// it is not read from a buffer — the CPU sets it explicitly before rendering.
uniform float u_time;

void main() {
    // Use the time value to animate the green channel.
    // sin() oscillates between -1 and 1, so we remap it to 0..1.
    float green = (sin(u_time) + 1.0) / 2.0;
    out_color = vec4(1.0, green, 0.2, 1.0);
}

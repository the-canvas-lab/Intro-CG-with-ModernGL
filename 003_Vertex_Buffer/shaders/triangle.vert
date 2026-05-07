#version 330 core

// The vertex position is now received as an input attribute fed from a buffer
// on the CPU side, rather than being hardcoded in the shader.
// Each invocation of this shader receives one vertex from the buffer.
in vec3 in_position;

void main() {
    gl_Position = vec4(in_position, 1.0);
}

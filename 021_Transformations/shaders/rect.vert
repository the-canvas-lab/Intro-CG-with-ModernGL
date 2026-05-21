#version 330 core

in vec3 in_position;
in vec2 in_uv;

out vec2 uv;

// A single 4×4 matrix encodes scale, rotation, and translation all at once.
// Multiplying every vertex by this matrix applies the full transformation.
uniform mat4 u_transform;

void main() {
    gl_Position = u_transform * vec4(in_position, 1.0);
    uv = in_uv;
}

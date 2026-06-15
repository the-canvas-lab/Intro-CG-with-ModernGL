#version 330 core

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_normal;

// A uniform BLOCK backed by a buffer (UBO). std140 fixes the memory layout
// so the CPU can write bytes that every program interprets identically.
//
// std140 offsets here:   mat4 view        -> bytes   0.. 63
//                        mat4 projection  -> bytes  64 ..127
layout (std140) uniform Matrices {
    mat4 view;
    mat4 projection;
};

// Per-object data stays a plain uniform - only data SHARED by many programs
// belongs in a UBO.
uniform mat4 model;

out vec3 frag_pos;
out vec3 normal;

void main() {
    frag_pos = vec3(model * vec4(in_position, 1.0));
    normal   = mat3(model) * in_normal;   // fine here: rotations only
    gl_Position = projection * view * vec4(frag_pos, 1.0);
}

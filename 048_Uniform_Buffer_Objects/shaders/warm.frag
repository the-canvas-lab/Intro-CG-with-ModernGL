#version 330 core

layout (location = 0) out vec4 out_color;

in vec3 frag_pos;
in vec3 normal;

// The same block declaration appears in BOTH fragment shaders. Because both
// programs bind the block to binding point 1, one buffer write on the CPU
// updates the lighting of every object, no matter which program draws it.
//
// std140 gotcha: vec3 is aligned to 16 bytes, so light_color does NOT start
// at byte 12 - it starts at byte 16. The CPU must write the padding.
//
//   vec3 light_dir    -> bytes  0..11   (+ 4 padding bytes)
//   vec3 light_color  -> bytes 16..27   (+ 4 padding bytes)
layout (std140) uniform LightBlock {
    vec3 light_dir;
    vec3 light_color;
};

void main() {
    float diff = max(dot(normalize(normal), -normalize(light_dir)), 0.0);
    vec3 base  = vec3(0.85, 0.45, 0.25);   // warm clay
    out_color  = vec4((0.25 + diff) * light_color * base, 1.0);
}

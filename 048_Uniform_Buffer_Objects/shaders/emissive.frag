#version 330 core

layout (location = 0) out vec4 out_color;

in vec3 frag_pos;
in vec3 normal;

// Identical block to warm.frag - same binding point, same buffer, zero
// duplicate uploads. Only the shading STYLE differs between the programs.
layout (std140) uniform LightBlock {
    vec3 light_dir;
    vec3 light_color;
};

void main() {
    out_color = vec4(light_color, 1.0);
}

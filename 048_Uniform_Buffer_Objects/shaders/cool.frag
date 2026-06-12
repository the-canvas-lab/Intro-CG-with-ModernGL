#version 330 core

layout (location = 0) out vec4 out_color;

in vec3 frag_pos;
in vec3 normal;

// Identical block to warm.frag — same binding point, same buffer, zero
// duplicate uploads. Only the shading STYLE differs between the programs.
layout (std140) uniform LightBlock {
    vec3 light_dir;
    vec3 light_color;
};

void main() {
    float diff = max(dot(normalize(normal), -normalize(light_dir)), 0.0);
    diff = floor(diff * 4.0) / 4.0;        // toon-style banding
    vec3 base = vec3(0.30, 0.50, 0.90);    // cool porcelain
    out_color = vec4((0.25 + diff) * light_color * base, 1.0);
}

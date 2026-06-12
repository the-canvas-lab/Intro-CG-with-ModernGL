#version 330 core

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec2 in_uv;

uniform mat4 model;       // billboard transform, rebuilt on the CPU each frame
uniform mat4 view;
uniform mat4 projection;

out vec3 frag_pos;
out vec2 tex_coords;

void main() {
    frag_pos   = vec3(model * vec4(in_position, 1.0));
    tex_coords = in_uv;
    gl_Position = projection * view * vec4(frag_pos, 1.0);
}

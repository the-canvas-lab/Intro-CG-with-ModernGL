#version 330 core

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec2 in_uv;

uniform mat4 view;
uniform mat4 projection;

out vec2 tex_coords;

void main() {
    tex_coords  = in_uv;
    gl_Position = projection * view * vec4(in_position, 1.0);
}

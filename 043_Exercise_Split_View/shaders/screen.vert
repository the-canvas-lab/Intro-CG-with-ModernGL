#version 330 core

in vec2 in_position;
in vec2 in_uv;

out vec2 tex_coords;

void main() {
    tex_coords  = in_uv;
    gl_Position = vec4(in_position, 0.0, 1.0);
}

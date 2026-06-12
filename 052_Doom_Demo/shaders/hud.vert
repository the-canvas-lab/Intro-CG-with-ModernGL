#version 330 core

layout (location = 0) in vec2 in_position;  // unit quad, -0.5 .. 0.5
layout (location = 1) in vec2 in_uv;

// 2D overlay: no matrices, just scale + offset straight into NDC.
uniform vec2 u_pos;
uniform vec2 u_scale;

out vec2 tex_coords;

void main() {
    tex_coords  = in_uv;
    gl_Position = vec4(in_position * u_scale + u_pos, 0.0, 1.0);
}

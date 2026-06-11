#version 330 core

in vec3 in_position;
in vec3 in_normal;
in vec2 in_uv;

out vec3 normal;
out vec2 tex_coords;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat3 normal_matrix;

void main() {
    normal      = normal_matrix * in_normal;
    tex_coords  = in_uv;
    gl_Position = projection * view * model * vec4(in_position, 1.0);
}

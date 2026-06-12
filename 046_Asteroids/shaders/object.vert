#version 330 core

in vec3 in_position;
in vec3 in_normal;
in vec2 in_uv;

out vec3 frag_normal;
out vec2 tex_coords;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    // Scale is uniform so mat3(model) is a valid normal matrix.
    frag_normal = mat3(model) * in_normal;
    tex_coords  = in_uv;
    gl_Position = projection * view * model * vec4(in_position, 1.0);
}

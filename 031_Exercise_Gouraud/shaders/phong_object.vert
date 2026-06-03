#version 330 core

in vec3 in_position;
in vec3 in_normal;

out vec3 frag_pos;
out vec3 normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat3 normal_matrix;

void main() {
    vec4 world_pos = model * vec4(in_position, 1.0);
    frag_pos = vec3(world_pos);
    normal   = normal_matrix * in_normal;
    gl_Position = projection * view * world_pos;
}

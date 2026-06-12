#version 330 core

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec2 in_uv;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat3 normal_matrix;
uniform mat4 u_light_space;

out vec3 frag_pos;
out vec3 normal;
out vec2 tex_coords;
out vec4 light_space_pos;   // this fragment, as the LIGHT saw it in pass 1

void main() {
    frag_pos        = vec3(model * vec4(in_position, 1.0));
    normal          = normal_matrix * in_normal;
    tex_coords      = in_uv;
    light_space_pos = u_light_space * vec4(frag_pos, 1.0);
    gl_Position     = projection * view * vec4(frag_pos, 1.0);
}

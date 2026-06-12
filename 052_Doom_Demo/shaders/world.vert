#version 330 core

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec2 in_uv;

uniform mat4 view;
uniform mat4 projection;

out vec3 frag_pos;
out vec3 normal;
out vec2 tex_coords;

void main() {
    // The maze geometry is baked directly in world space (the map never
    // moves), so there is no model matrix — world position IS the attribute.
    frag_pos   = in_position;
    normal     = in_normal;
    tex_coords = in_uv;
    gl_Position = projection * view * vec4(in_position, 1.0);
}

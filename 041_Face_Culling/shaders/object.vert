#version 330 core

in vec3 in_position;
in vec2 in_uv;
in float in_face_id;

out vec2 tex_coords;
out float face_id;   // constant across each face, so interpolation is exact

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main() {
    tex_coords  = in_uv;
    face_id     = in_face_id;
    gl_Position = projection * view * model * vec4(in_position, 1.0);
}

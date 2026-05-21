#version 330 core

in vec3 in_position;
in vec2 in_uv;

out vec2 uv;

uniform mat4 u_transform;

void main() {
    gl_Position = u_transform * vec4(in_position, 1.0);
    uv = in_uv;
}

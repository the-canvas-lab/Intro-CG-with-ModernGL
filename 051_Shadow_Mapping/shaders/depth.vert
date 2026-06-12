#version 330 core

layout (location = 0) in vec3 in_position;

// Pass 1: render the scene from the LIGHT's point of view. Only depth is
// needed, so the "camera" matrices are replaced by one light-space matrix
// (orthographic projection * lookAt from the light).
uniform mat4 u_light_space;
uniform mat4 model;

void main() {
    gl_Position = u_light_space * model * vec4(in_position, 1.0);
}

#version 330 core

in vec3 in_position;

out vec3 tex_dir;

uniform mat4 view;
uniform mat4 projection;

void main() {
    // The vertex position is used directly as the cubemap sample direction.
    tex_dir = in_position;

    // Strip translation from the view matrix so the skybox stays centred on
    // the camera regardless of its world position.  Setting z = w forces the
    // depth to 1.0 after the perspective divide, placing the skybox at the far
    // plane and behind all scene geometry.
    vec4 pos    = projection * mat4(mat3(view)) * vec4(in_position, 1.0);
    gl_Position = pos.xyww;
}

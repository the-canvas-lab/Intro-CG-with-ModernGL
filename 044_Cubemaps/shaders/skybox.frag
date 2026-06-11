#version 330 core

layout (location = 0) out vec4 out_color;

in vec3 tex_dir;

uniform samplerCube u_skybox;

void main() {
    out_color = texture(u_skybox, tex_dir);
}

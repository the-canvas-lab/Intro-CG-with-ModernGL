#version 330 core

layout (location = 0) out vec4 out_color;

in vec2 tex_coords;

uniform sampler2D u_screen;

void main() {
    out_color = texture(u_screen, tex_coords);
}

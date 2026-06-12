#version 330 core

layout (location = 0) out vec4 out_color;

in vec2 tex_coords;

uniform sampler2D u_texture;
uniform vec4      u_color;     // flat color, or tint when textured
uniform bool      u_textured;

void main() {
    if (u_textured) {
        out_color = texture(u_texture, tex_coords) * u_color;
    } else {
        out_color = u_color;
    }
}

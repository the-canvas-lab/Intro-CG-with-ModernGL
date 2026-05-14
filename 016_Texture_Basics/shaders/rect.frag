#version 330 core

layout (location = 0) out vec4 out_color;

in vec2 uv;

// A sampler2D uniform tells the shader which texture unit to read from.
// The CPU sets it to an integer (the unit number, e.g. 0) before drawing.
uniform sampler2D u_texture;

void main() {
    // texture() looks up the color in u_texture at the interpolated UV coordinate.
    out_color = texture(u_texture, uv);
}

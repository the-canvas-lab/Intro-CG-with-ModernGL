#version 330 core

layout (location = 0) out vec4 out_color;

in vec2 tex_coords;

uniform sampler2D u_texture;

void main() {
    // gl_FrontFacing is true when the fragment belongs to a front-facing triangle
    // (one whose vertices wind counter-clockwise as seen from the camera).
    // Back-facing fragments are coloured solid blue so their presence or absence
    // is immediately visible when switching cull modes.
    if (gl_FrontFacing) {
        out_color = texture(u_texture, tex_coords);
    } else {
        out_color = vec4(0.2, 0.4, 1.0, 1.0);
    }
}

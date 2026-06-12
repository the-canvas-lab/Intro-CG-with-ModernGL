#version 330 core

layout (location = 0) out vec4 out_color;

in vec2 tex_coords;

uniform sampler2D u_texture;

// Nothing special here on purpose: mip level selection is AUTOMATIC.
// The GPU compares how fast tex_coords change between neighbouring pixels
// (screen-space UV derivatives) and picks the mip level whose texels map
// roughly 1:1 onto pixels. The whole lesson lives in the texture's
// min-filter setting on the CPU side.
void main() {
    out_color = texture(u_texture, tex_coords);
}

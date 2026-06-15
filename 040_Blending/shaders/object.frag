#version 330 core

layout (location = 0) out vec4 out_color;

in vec2 tex_coords;

uniform sampler2D u_texture;

void main() {
    // Output the full RGBA value - the GPU's blend unit composites it
    // against whatever is already in the framebuffer using the blend
    // function set on the CPU side:
    //   result = src_alpha * src_color + (1 - src_alpha) * dst_color
    out_color = texture(u_texture, tex_coords);
}

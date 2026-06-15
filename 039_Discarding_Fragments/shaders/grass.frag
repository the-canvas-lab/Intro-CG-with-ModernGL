#version 330 core

layout (location = 0) out vec4 out_color;

in vec2 tex_coords;

uniform sampler2D u_texture;

void main() {
    vec4 tex_color = texture(u_texture, tex_coords);

    // Throw away fragments whose alpha falls below the threshold.
    // The depth buffer is not written for discarded fragments, so
    // no depth sorting is needed - unlike true alpha blending.
    if (tex_color.a < 0.1)
        discard;

    out_color = tex_color;
}

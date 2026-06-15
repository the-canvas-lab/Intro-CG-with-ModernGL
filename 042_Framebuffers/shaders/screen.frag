#version 330 core

layout (location = 0) out vec4 out_color;

in vec2 tex_coords;

uniform sampler2D u_screen;
uniform int u_mode;

const float OFFSET = 1.0 / 300.0;

vec2 offsets[9] = vec2[](
    vec2(-OFFSET,  OFFSET), vec2(0.0,  OFFSET), vec2(OFFSET,  OFFSET),
    vec2(-OFFSET,  0.0   ), vec2(0.0,  0.0   ), vec2(OFFSET,  0.0   ),
    vec2(-OFFSET, -OFFSET), vec2(0.0, -OFFSET), vec2(OFFSET, -OFFSET)
);

vec3 sample_kernel(float kernel[9]) {
    vec3 col = vec3(0.0);
    for (int i = 0; i < 9; i++)
        col += texture(u_screen, tex_coords + offsets[i]).rgb * kernel[i];
    return col;
}

void main() {
    vec3 col = texture(u_screen, tex_coords).rgb;

    if (u_mode == 0) {
        // Passthrough - show the offscreen texture unchanged.
        out_color = vec4(col, 1.0);

    } else if (u_mode == 1) {
        // Inversion - flip each channel around 0.5.
        out_color = vec4(1.0 - col, 1.0);

    } else if (u_mode == 2) {
        // Grayscale - weighted luminance (ITU-R BT.601 coefficients).
        float grey = dot(col, vec3(0.2126, 0.7152, 0.0722));
        out_color = vec4(vec3(grey), 1.0);

    } else if (u_mode == 3) {
        // Sharpen - centre gets +5, each cardinal neighbour gets -1.
        float kernel[9] = float[](
            -1.0, -1.0, -1.0,
            -1.0,  9.0, -1.0,
            -1.0, -1.0, -1.0
        );
        out_color = vec4(sample_kernel(kernel), 1.0);

    } else if (u_mode == 4) {
        // Blur - uniform 3×3 box filter (each weight = 1/9).
        float kernel[9] = float[](
            1.0/9.0, 1.0/9.0, 1.0/9.0,
            1.0/9.0, 1.0/9.0, 1.0/9.0,
            1.0/9.0, 1.0/9.0, 1.0/9.0
        );
        out_color = vec4(sample_kernel(kernel), 1.0);

    } else {
        // Edge detection - Laplacian-like kernel; edges are bright on black.
        float kernel[9] = float[](
             1.0,  1.0,  1.0,
             1.0, -8.0,  1.0,
             1.0,  1.0,  1.0
        );
        out_color = vec4(sample_kernel(kernel), 1.0);
    }
}

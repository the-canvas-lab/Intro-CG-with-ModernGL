#version 330 core

layout (location = 0) out vec4 out_color;

in vec2 tex_coords;

uniform sampler2D u_screen;

void main() {
    vec3 col = texture(u_screen, tex_coords).rgb;

    // TODO — Convert col to grayscale and assign the result to out_color.
    //
    // Human eyes are not equally sensitive to each colour channel.
    // Use a weighted dot product (ITU-R BT.601 luminance coefficients):
    //
    //   R: 0.2126   G: 0.7152   B: 0.0722
    //
    // The result is a single float; expand it back to vec4 for out_color.
}

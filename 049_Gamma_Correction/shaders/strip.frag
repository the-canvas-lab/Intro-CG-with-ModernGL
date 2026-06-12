#version 330 core

layout (location = 0) out vec4 out_color;

in vec2 tex_coords;

uniform bool u_gamma;

// A mathematically linear brightness ramp from 0 to 1.
//
// Without correction the monitor applies its ~2.2 curve and the ramp LOOKS
// wrong: the physical 50%-light point appears around 73% of the way along.
// With correction, halfway along the strip really emits half the photons.
void main() {
    float v = tex_coords.x;
    if (u_gamma) {
        v = pow(v, 1.0 / 2.2);
    }
    out_color = vec4(vec3(v), 1.0);
}

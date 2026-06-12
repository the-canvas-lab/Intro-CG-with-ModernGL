#version 330 core

layout (location = 0) out vec4 out_color;

in vec3 frag_pos;
in vec3 normal;
in vec2 tex_coords;

uniform sampler2D u_texture;
uniform vec3 light_positions[3];
uniform vec3 light_colors[3];
uniform bool u_gamma;

void main() {
    vec3 tex = texture(u_texture, tex_coords).rgb;

    // The texture was AUTHORED on a gamma display, so its pixel values are
    // sRGB-encoded. To light it correctly we must first decode to linear
    // space. (Drivers can do this for free via an SRGB internal format;
    // doing it explicitly keeps the math visible.)
    if (u_gamma) {
        tex = pow(tex, vec3(2.2));
    }

    vec3 result = 0.05 * tex;   // small ambient
    vec3 n = normalize(normal);

    for (int i = 0; i < 3; i++) {
        vec3  to_light = light_positions[i] - frag_pos;
        float dist     = length(to_light);
        float diff     = max(dot(n, normalize(to_light)), 0.0);

        // In linear space the physically correct inverse-square law looks
        // right. Without gamma correction it looks far too dark, which is
        // why pre-gamma engines faked it with 1/d falloff.
        float atten = u_gamma ? 1.0 / (dist * dist)
                              : 1.0 / dist;

        result += diff * atten * light_colors[i] * tex;
    }

    // Final encode: monitors darken what they show (~pow 2.2), so we
    // pre-brighten by the inverse. Apply ONLY at the very end, only once.
    if (u_gamma) {
        result = pow(result, vec3(1.0 / 2.2));
    }
    out_color = vec4(result, 1.0);
}

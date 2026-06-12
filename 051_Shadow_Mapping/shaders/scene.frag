#version 330 core

layout (location = 0) out vec4 out_color;

in vec3 frag_pos;
in vec3 normal;
in vec2 tex_coords;
in vec4 light_space_pos;

uniform sampler2D u_texture;      // unit 0
uniform sampler2D u_shadow_map;   // unit 1: pass-1 depth from the light
uniform vec3 u_light_dir;         // direction TOWARD the light (normalized)
uniform bool u_use_bias;
uniform bool u_use_pcf;

// Returns 1.0 if this fragment is in shadow, 0.0 if lit.
//
// Core idea: project the fragment into the light's clip space and compare
// its depth with what the light actually saw there (the shadow map). If
// something nearer to the light was recorded, this fragment is occluded.
float shadow_factor(vec3 n, vec3 l) {
    // Perspective divide + map from NDC [-1,1] to texture space [0,1].
    vec3 p = light_space_pos.xyz / light_space_pos.w;
    p = p * 0.5 + 0.5;

    // Outside the light's frustum nothing was recorded — treat as lit.
    if (p.z > 1.0 || p.x < 0.0 || p.x > 1.0 || p.y < 0.0 || p.y > 1.0) {
        return 0.0;
    }

    // Shadow ACNE: the map's resolution is finite, so a surface sampled at
    // a slight angle zig-zags above and below its own recorded depth and
    // shadows itself in stripes. A small depth bias — larger at grazing
    // angles — pushes the comparison past the noise. (Toggle B to see it.)
    float bias = u_use_bias ? max(0.05 * (1.0 - dot(n, l)), 0.005) : 0.0;

    if (u_use_pcf) {
        // PCF (percentage-closer filtering): average the comparison over a
        // 3x3 neighbourhood. Note it averages COMPARISONS, not depths —
        // averaging depths first would be meaningless. (Toggle P.)
        vec2 texel = 1.0 / vec2(textureSize(u_shadow_map, 0));
        float shadow = 0.0;
        for (int x = -1; x <= 1; x++) {
            for (int y = -1; y <= 1; y++) {
                float closest = texture(u_shadow_map, p.xy + vec2(x, y) * texel).r;
                shadow += (p.z - bias > closest) ? 1.0 : 0.0;
            }
        }
        return shadow / 9.0;
    }

    float closest = texture(u_shadow_map, p.xy).r;
    return (p.z - bias > closest) ? 1.0 : 0.0;
}

void main() {
    vec3 tex = texture(u_texture, tex_coords).rgb;
    vec3 n   = normalize(normal);
    vec3 l   = normalize(u_light_dir);

    float diff   = max(dot(n, l), 0.0);
    float shadow = shadow_factor(n, l);

    // Ambient stays — shadowed areas are darker, not black.
    vec3 color = (0.25 + (1.0 - shadow) * diff) * vec3(1.0, 0.96, 0.88) * tex;
    out_color = vec4(color, 1.0);
}

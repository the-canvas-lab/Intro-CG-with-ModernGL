#version 330 core

layout (location = 0) out vec4 out_color;

in vec3 frag_pos;
in vec3 normal;
in vec2 tex_coords;

// Spot light with attenuation — the player's flashlight (lessons 036/037).
struct Light {
    vec3  position;
    vec3  direction;
    float cut_off;       // cos of inner cone half-angle
    float outer_cut_off; // cos of outer cone half-angle
    vec3  ambient;
    vec3  diffuse;
    float constant;      // attenuation terms (lesson 036)
    float linear;
    float quadratic;
};

uniform Light     light;
uniform sampler2D u_texture;
uniform vec3      u_tint;    // lets walls / floor / ceiling share one texture

void main() {
    vec3 tex_color = texture(u_texture, tex_coords).rgb * u_tint;

    vec3 light_dir = normalize(light.position - frag_pos);

    // Soft spot cone (lesson 036)
    float theta     = dot(light_dir, normalize(-light.direction));
    float epsilon   = light.cut_off - light.outer_cut_off;
    float intensity = clamp((theta - light.outer_cut_off) / epsilon, 0.0, 1.0);

    // Distance attenuation (lesson 036)
    float dist  = length(light.position - frag_pos);
    float atten = 1.0 / (light.constant + light.linear * dist
                                        + light.quadratic * dist * dist);

    // Diffuse only — Doom-era walls are matte, no specular highlight.
    float diff = max(dot(normalize(normal), light_dir), 0.0);

    vec3 color = (light.ambient + light.diffuse * diff * intensity * atten) * tex_color;
    out_color = vec4(color, 1.0);
}

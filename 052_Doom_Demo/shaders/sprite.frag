#version 330 core

layout (location = 0) out vec4 out_color;

in vec3 frag_pos;
in vec2 tex_coords;

// Same flashlight struct as world.frag so one upload serves both programs.
struct Light {
    vec3  position;
    vec3  direction;
    float cut_off;
    float outer_cut_off;
    vec3  ambient;
    vec3  diffuse;
    float constant;
    float linear;
    float quadratic;
};

uniform Light     light;
uniform sampler2D u_texture;

void main() {
    vec4 tex = texture(u_texture, tex_coords);

    // Alpha cutout (lesson 039): transparent texels simply do not exist.
    // No depth write, no sorting — exactly how Doom drew its sprites.
    if (tex.a < 0.5) discard;

    // A sprite is a flat card with no meaningful normal, so it receives the
    // flashlight cone + attenuation but no diffuse angle term: enemies fade
    // out of the darkness as the beam sweeps over them.
    vec3 light_dir  = normalize(light.position - frag_pos);
    float theta     = dot(light_dir, normalize(-light.direction));
    float epsilon   = light.cut_off - light.outer_cut_off;
    float intensity = clamp((theta - light.outer_cut_off) / epsilon, 0.0, 1.0);

    float dist  = length(light.position - frag_pos);
    float atten = 1.0 / (light.constant + light.linear * dist
                                        + light.quadratic * dist * dist);

    vec3 color = (light.ambient + light.diffuse * intensity * atten) * tex.rgb;
    out_color = vec4(color, 1.0);
}

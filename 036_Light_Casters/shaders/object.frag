#version 330 core

layout (location = 0) out vec4 out_color;

in vec3 frag_pos;
in vec3 normal;
in vec2 tex_coords;

struct Material {
    sampler2D diffuse;
    sampler2D specular;
    float     shininess;
};

// All three light types share one struct.
// Fields used per mode:
//   Directional — direction
//   Point       — position, constant, linear, quadratic
//   Spot        — position, direction, cut_off, outer_cut_off
struct Light {
    vec3  direction;
    vec3  position;
    float cut_off;
    float outer_cut_off;
    float constant;
    float linear;
    float quadratic;
    vec3  ambient;
    vec3  diffuse;
    vec3  specular;
};

// 0 = Directional   1 = Point   2 = Spot
uniform int      u_mode;
uniform Material material;
uniform Light    light;
uniform vec3     u_view_pos;

void main() {
    vec3 diff_color = vec3(texture(material.diffuse,  tex_coords));
    vec3 spec_color = vec3(texture(material.specular, tex_coords));

    vec3  norm         = normalize(normal);
    vec3  view_dir     = normalize(u_view_pos - frag_pos);
    vec3  light_dir    = vec3(0.0);
    float attenuation  = 1.0;
    float intensity    = 1.0;

    if (u_mode == 0) {
        // Directional: the same direction for every fragment.
        light_dir = normalize(-light.direction);

    } else if (u_mode == 1) {
        // Point: direction from fragment to source, brightness falls with distance.
        light_dir    = normalize(light.position - frag_pos);
        float d      = length(light.position - frag_pos);
        attenuation  = 1.0 / (light.constant + light.linear * d + light.quadratic * d * d);

    } else {
        // Spot: same as point direction, but restricted to a cone.
        light_dir     = normalize(light.position - frag_pos);
        float theta   = dot(light_dir, normalize(-light.direction));
        float epsilon = light.cut_off - light.outer_cut_off;
        intensity     = clamp((theta - light.outer_cut_off) / epsilon, 0.0, 1.0);
    }

    // Ambient: fades with distance for point light; unchanged for the others.
    vec3 ambient = light.ambient * diff_color;
    if (u_mode == 1) ambient *= attenuation;

    float diff   = max(dot(norm, light_dir), 0.0);
    vec3 diffuse = light.diffuse * diff * diff_color;

    vec3 reflect_dir = reflect(-light_dir, norm);
    float spec       = pow(max(dot(view_dir, reflect_dir), 0.0), material.shininess);
    vec3 specular    = light.specular * spec * spec_color;

    diffuse  *= attenuation * intensity;
    specular *= attenuation * intensity;

    out_color = vec4(ambient + diffuse + specular, 1.0);
}

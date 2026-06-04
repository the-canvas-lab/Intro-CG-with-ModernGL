#version 330 core

layout (location = 0) out vec4 out_color;

in vec3 frag_pos;
in vec3 normal;
in vec2 tex_coords;

// material.diffuse  - sampler bound to unit 0 (container2.png)
// material.specular - sampler bound to unit 1 (container2_specular.png)
struct Material {
    sampler2D diffuse;
    sampler2D specular;
    float     shininess;
};

struct Light {
    vec3 position;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

uniform Material material;
uniform Light    light;
uniform vec3     u_view_pos;

void main() {
    vec3 diff_color = vec3(texture(material.diffuse,  tex_coords));
    vec3 spec_color = vec3(texture(material.specular, tex_coords));

    // Ambient uses the diffuse map - no separate ambient texture needed.
    vec3 ambient = light.ambient * diff_color;

    vec3 norm      = normalize(normal);
    vec3 light_dir = normalize(light.position - frag_pos);
    float diff     = max(dot(norm, light_dir), 0.0);
    vec3 diffuse   = light.diffuse * diff * diff_color;

    vec3 view_dir    = normalize(u_view_pos - frag_pos);
    vec3 reflect_dir = reflect(-light_dir, norm);
    float spec       = pow(max(dot(view_dir, reflect_dir), 0.0), material.shininess);
    vec3 specular    = light.specular * spec * spec_color;

    out_color = vec4(ambient + diffuse + specular, 1.0);
}

#version 330 core

layout (location = 0) out vec4 out_color;

in vec3 frag_pos;
in vec3 normal;
in vec2 tex_coords;

struct Material {
    sampler2D diffuse;
    sampler2D specular;
    // TODO 1 — add a sampler2D emission field here
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

    vec3 ambient = light.ambient * diff_color;

    vec3 norm      = normalize(normal);
    vec3 light_dir = normalize(light.position - frag_pos);
    float diff     = max(dot(norm, light_dir), 0.0);
    vec3 diffuse   = light.diffuse * diff * diff_color;

    vec3 view_dir    = normalize(u_view_pos - frag_pos);
    vec3 reflect_dir = reflect(-light_dir, norm);
    float spec       = pow(max(dot(view_dir, reflect_dir), 0.0), material.shininess);
    vec3 specular    = light.specular * spec * spec_color;

    // TODO 2 — sample the emission map and add it to out_color.
    //   vec3 emission = vec3(texture(material.emission, tex_coords));
    //   out_color = vec4(ambient + diffuse + specular + emission, 1.0);
    out_color = vec4(ambient + diffuse + specular, 1.0);
}

#version 330 core

layout (location = 0) out vec4 out_color;

in vec3 frag_pos;
in vec3 normal;

struct Material {
    vec3  ambient;
    vec3  diffuse;
    vec3  specular;
    float shininess;
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

// 0 = ambient only   1 = diffuse only   2 = specular only   3 = full Phong
uniform int u_mode;

void main() {
    vec3 ambient = light.ambient * material.ambient;

    vec3 norm      = normalize(normal);
    vec3 light_dir = normalize(light.position - frag_pos);
    float diff     = max(dot(norm, light_dir), 0.0);
    vec3 diffuse   = light.diffuse * (diff * material.diffuse);

    vec3 view_dir    = normalize(u_view_pos - frag_pos);
    vec3 reflect_dir = reflect(-light_dir, norm);
    float spec       = pow(max(dot(view_dir, reflect_dir), 0.0), material.shininess);
    vec3 specular    = light.specular * (spec * material.specular);

    if      (u_mode == 0) out_color = vec4(ambient,                     1.0);
    else if (u_mode == 1) out_color = vec4(diffuse,                     1.0);
    else if (u_mode == 2) out_color = vec4(specular,                    1.0);
    else                  out_color = vec4(ambient + diffuse + specular, 1.0);
}

#version 330 core

layout (location = 0) out vec4 out_color;

in vec3 frag_pos;
in vec3 normal;

// Material describes how the surface reacts to each lighting component.
struct Material {
    vec3  ambient;    // colour under ambient light
    vec3  diffuse;    // colour under diffuse light
    vec3  specular;   // colour of the specular highlight
    float shininess;  // controls the size of the highlight: higher = sharper
};

// Light carries separate intensities for each component.
// This lets ambient be dim while specular is full-bright.
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
    vec3 ambient = light.ambient * material.ambient;

    vec3 norm      = normalize(normal);
    vec3 light_dir = normalize(light.position - frag_pos);
    float diff     = max(dot(norm, light_dir), 0.0);
    vec3 diffuse   = light.diffuse * (diff * material.diffuse);

    vec3 view_dir    = normalize(u_view_pos - frag_pos);
    vec3 reflect_dir = reflect(-light_dir, norm);
    float spec       = pow(max(dot(view_dir, reflect_dir), 0.0), material.shininess);
    vec3 specular    = light.specular * (spec * material.specular);

    out_color = vec4(ambient + diffuse + specular, 1.0);
}

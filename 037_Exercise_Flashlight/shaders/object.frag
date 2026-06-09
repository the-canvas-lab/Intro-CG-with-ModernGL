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

struct Light {
    vec3  position;
    vec3  direction;     // direction the cone points toward
    float cut_off;       // cos of inner cone half-angle
    float outer_cut_off; // cos of outer cone half-angle (soft edge begins here)
    vec3  ambient;
    vec3  diffuse;
    vec3  specular;
};

uniform Material material;
uniform Light    light;
uniform vec3     u_view_pos;

void main() {
    vec3 diff_color = vec3(texture(material.diffuse,  tex_coords));
    vec3 spec_color = vec3(texture(material.specular, tex_coords));

    vec3 light_dir = normalize(light.position - frag_pos);

    // Smooth spot intensity using the angle between the fragment direction and the cone axis.
    //   theta > cut_off        → inside inner cone  → intensity 1
    //   theta < outer_cut_off  → outside outer cone → intensity 0
    //   in between             → smooth gradient
    float theta     = dot(light_dir, normalize(-light.direction));
    float epsilon   = light.cut_off - light.outer_cut_off;
    float intensity = clamp((theta - light.outer_cut_off) / epsilon, 0.0, 1.0);

    vec3 ambient = light.ambient * diff_color;

    vec3 norm  = normalize(normal);
    float diff = max(dot(norm, light_dir), 0.0);
    vec3 diffuse = light.diffuse * diff * diff_color;

    vec3 view_dir    = normalize(u_view_pos - frag_pos);
    vec3 reflect_dir = reflect(-light_dir, norm);
    float spec       = pow(max(dot(view_dir, reflect_dir), 0.0), material.shininess);
    vec3 specular    = light.specular * spec * spec_color;

    // Ambient is unchanged — fragments outside the cone still receive base light.
    diffuse  *= intensity;
    specular *= intensity;

    out_color = vec4(ambient + diffuse + specular, 1.0);
}

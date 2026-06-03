#version 330 core

layout (location = 0) out vec4 out_color;

in vec3 frag_pos;
in vec3 normal;

const int NUM_MATERIALS = 8;

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

// All 8 materials are resident on the GPU.  Only the index changes at runtime.
uniform Material materials[NUM_MATERIALS];
uniform int      u_material_index;

uniform Light light;
uniform vec3  u_view_pos;

void main() {
    // Select the active material by indexing into the uniform array.
    // Dynamic (non-constant) indexing of uniform arrays is valid in GLSL 3.30.
    Material mat = materials[u_material_index];

    vec3 ambient = light.ambient * mat.ambient;

    vec3 norm      = normalize(normal);
    vec3 light_dir = normalize(light.position - frag_pos);
    float diff     = max(dot(norm, light_dir), 0.0);
    vec3 diffuse   = light.diffuse * (diff * mat.diffuse);

    vec3 view_dir    = normalize(u_view_pos - frag_pos);
    vec3 reflect_dir = reflect(-light_dir, norm);
    float spec       = pow(max(dot(view_dir, reflect_dir), 0.0), mat.shininess);
    vec3 specular    = light.specular * (spec * mat.specular);

    out_color = vec4(ambient + diffuse + specular, 1.0);
}

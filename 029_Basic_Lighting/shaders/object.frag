#version 330 core

layout (location = 0) out vec4 out_color;

in vec3 frag_pos;
in vec3 normal;

uniform vec3 u_object_color;
uniform vec3 u_light_color;
uniform vec3 u_light_pos;
uniform vec3 u_view_pos;

void main() {
    // --- Ambient ---
    // A constant minimum brightness that approximates indirect/scattered light.
    float ambient_strength = 0.1;
    vec3 ambient = ambient_strength * u_light_color;

    // --- Diffuse ---
    // Brightness proportional to how directly the surface faces the light.
    // dot(normal, lightDir) = cos(angle): 1.0 when facing head-on, 0.0 at 90°.
    // max(..., 0.0) prevents negative values when the light is behind the surface.
    vec3 norm      = normalize(normal);
    vec3 light_dir = normalize(u_light_pos - frag_pos);
    float diff     = max(dot(norm, light_dir), 0.0);
    vec3 diffuse   = diff * u_light_color;

    // --- Specular ---
    // A sharp highlight visible when the reflection vector points toward the viewer.
    // The shininess exponent (32) controls how focused the highlight is -
    // higher values produce a smaller, shinier spot.
    float specular_strength = 0.5;
    vec3 view_dir    = normalize(u_view_pos - frag_pos);
    vec3 reflect_dir = reflect(-light_dir, norm);
    float spec       = pow(max(dot(view_dir, reflect_dir), 0.0), 32.0);
    vec3 specular    = specular_strength * spec * u_light_color;

    out_color = vec4((ambient + diffuse + specular) * u_object_color, 1.0);
}

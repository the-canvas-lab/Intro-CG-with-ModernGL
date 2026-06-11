#version 330 core

layout (location = 0) out vec4 out_color;

in vec3 normal;
in vec2 tex_coords;

uniform sampler2D u_texture;

void main() {
    vec3 light_dir  = normalize(vec3(1.0, 2.0, 3.0));
    float diffuse   = max(dot(normalize(normal), light_dir), 0.0);
    vec3 tex        = texture(u_texture, tex_coords).rgb;
    out_color       = vec4(tex * (0.3 + 0.7 * diffuse), 1.0);
}

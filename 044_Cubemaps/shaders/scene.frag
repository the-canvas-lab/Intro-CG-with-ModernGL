#version 330 core

layout (location = 0) out vec4 out_color;

in vec3 frag_pos;
in vec3 normal;
in vec2 tex_coords;

uniform sampler2D   u_texture;
uniform samplerCube u_skybox;
uniform vec3        u_camera_pos;
uniform int         u_mode;

void main() {
    vec3 N = normalize(normal);
    vec3 I = normalize(frag_pos - u_camera_pos);

    if (u_mode == 0) {
        // Textured with a simple directional light.
        vec3 light_dir = normalize(vec3(1.0, 2.0, 3.0));
        float diffuse  = max(dot(N, light_dir), 0.0);
        vec3 tex       = texture(u_texture, tex_coords).rgb;
        out_color      = vec4(tex * (0.3 + 0.7 * diffuse), 1.0);

    } else if (u_mode == 1) {
        // Environment reflection: mirror the incident ray about the surface normal.
        vec3 R    = reflect(I, N);
        out_color = vec4(texture(u_skybox, R).rgb, 1.0);

    } else {
        // Environment refraction: bend the incident ray as it passes through the
        // surface.  The ratio 1.0/1.52 models air-to-glass (Snell's law).
        vec3 R    = refract(I, N, 1.0 / 1.52);
        out_color = vec4(texture(u_skybox, R).rgb, 1.0);
    }
}

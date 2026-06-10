#version 330 core

layout (location = 0) out vec4 out_color;

in vec3 normal;
in vec2 tex_coords;

uniform sampler2D u_texture;
uniform int       u_mode;
uniform float     u_near;
uniform float     u_far;

void main() {
    if (u_mode == 0) {
        // Simple directional shading so the cubes read as 3D objects.
        vec3 norm      = normalize(normal);
        vec3 light_dir = normalize(vec3(1.0, 1.0, 1.0));
        float diff     = max(dot(norm, light_dir), 0.0);
        vec3 color     = texture(u_texture, tex_coords).rgb;
        out_color      = vec4((0.2 + 0.8 * diff) * color, 1.0);

    } else if (u_mode == 1) {
        // Raw depth stored in the depth buffer.
        // Values are in [0, 1] but distributed non-linearly: most of the
        // precision sits near the near plane, so distant objects cluster
        // near 1.0 and appear almost uniformly white.
        out_color = vec4(vec3(gl_FragCoord.z), 1.0);

    } else {
        // Linearize depth back to view-space distance, then normalize by far
        // so the result still sits in [0, 1] for display.
        //
        // gl_FragCoord.z is in [0, 1]. Convert to NDC [-1, 1] first, then
        // apply the inverse of the perspective depth formula:
        //   linear = (2 * near * far) / (far + near - z_ndc * (far - near))
        float z_ndc = gl_FragCoord.z * 2.0 - 1.0;
        float linear = (2.0 * u_near * u_far) / (u_far + u_near - z_ndc * (u_far - u_near));
        out_color = vec4(vec3(linear / u_far), 1.0);
    }
}

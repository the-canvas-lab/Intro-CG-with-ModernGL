#version 330 core

layout (location = 0) out vec4 out_color;

in vec2 tex_coords;

uniform sampler2D u_depth;

// Visualize the raw shadow map: white = far, black = near the light.
// With an ORTHOGRAPHIC light projection depth is already linear, so no
// un-projection is needed (compare lesson 038, where perspective depth
// had to be linearized first).
void main() {
    float d = texture(u_depth, tex_coords).r;
    out_color = vec4(vec3(d), 1.0);
}

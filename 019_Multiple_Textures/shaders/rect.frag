#version 330 core

layout (location = 0) out vec4 out_color;

in vec2 uv;

uniform sampler2D u_texture0;
uniform sampler2D u_texture1;

void main() {
    // mix(a, b, t) returns a*(1-t) + b*t.
    // At t=0.2 the container is 80% visible and the face is 20% visible.
    out_color = mix(texture(u_texture0, uv), texture(u_texture1, uv), 0.2);
}

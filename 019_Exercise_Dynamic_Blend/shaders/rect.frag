#version 330 core

layout (location = 0) out vec4 out_color;

in vec2 uv;

uniform sampler2D u_texture0;
uniform sampler2D u_texture1;

// TODO: Add a uniform float u_mix here.
//       The CPU will write a new value every frame based on key input.

void main() {
    // TODO: Replace 0.2 with u_mix so the blend ratio becomes dynamic.
    out_color = mix(texture(u_texture0, uv), texture(u_texture1, uv), 0.2);
}

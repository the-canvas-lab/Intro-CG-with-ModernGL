#version 330 core

in vec3 in_position;
in vec3 in_normal;
in vec2 in_uv;

// Per-instance model matrix split into four vec4 columns.
// OpenGL requires each attribute location to hold at most a vec4, so a mat4
// must be split manually and reassembled here.
in vec4 in_model_c0;
in vec4 in_model_c1;
in vec4 in_model_c2;
in vec4 in_model_c3;

out vec3 frag_normal;
out vec2 tex_coords;

uniform mat4 view;
uniform mat4 projection;

void main() {
    mat4 model  = mat4(in_model_c0, in_model_c1, in_model_c2, in_model_c3);

    // Upper-left 3×3 is a valid normal matrix for uniform scale.
    frag_normal = mat3(in_model_c0.xyz, in_model_c1.xyz, in_model_c2.xyz) * in_normal;
    tex_coords  = in_uv;
    gl_Position = projection * view * model * vec4(in_position, 1.0);
}

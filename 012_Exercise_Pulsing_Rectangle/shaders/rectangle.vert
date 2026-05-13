#version 330 core

in vec3 in_position;

// TODO: Declare 'in_color' as a per-vertex input attribute (vec3).

// TODO: Declare 'v_color' as an output to the fragment shader (vec3).

// TODO: Declare 'u_time' as a float uniform.

void main() {
    gl_Position = vec4(in_position, 1.0);

    // TODO: Compute 'brightness' from u_time using sin(), remapped to 0..1.
    //       Multiply in_color by brightness and assign the result to v_color.
    //       Think about what happens to the black vertices — why do they stay black?
}

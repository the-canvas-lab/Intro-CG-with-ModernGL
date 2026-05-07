#version 330 core

in vec3 in_position;

// TODO: Declare a second input attribute 'in_color' of type vec3 to receive
//       the per-vertex color from the buffer.

// TODO: Declare an output variable 'v_color' of type vec3 to pass the color
//       to the fragment shader.

void main() {
    gl_Position = vec4(in_position, 1.0);

    // TODO: Pass 'in_color' through to 'v_color'.
}

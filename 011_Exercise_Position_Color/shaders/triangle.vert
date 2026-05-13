#version 330 core

in vec3 in_position;

// TODO: Declare an output variable 'v_color' of type vec3.

void main() {
    gl_Position = vec4(in_position, 1.0);

    // TODO: Assign in_position directly to v_color.
    //       Then observe the result and think about why parts of the triangle
    //       appear black even though no vertex was explicitly colored black.
}

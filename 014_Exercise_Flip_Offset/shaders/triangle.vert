#version 330 core

in vec3 in_position;

uniform vec2 u_offset;

void main() {
    // TODO 1: Flip the triangle vertically by negating the y component of
    //         in_position before passing it to gl_Position.

    // TODO 2: Apply u_offset to shift the triangle horizontally and vertically.
    //         Add u_offset to the x and y components of the position.

    gl_Position = vec4(in_position, 1.0);
}

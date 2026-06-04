#version 330 core

layout (location = 0) out vec4 out_color;

uniform vec3 u_object_color;
uniform vec3 u_light_color;

void main() {
    // An object's perceived color is the component-wise product of the
    // light's color and the object's own reflectance.
    //
    // Example: coral (1.0, 0.5, 0.31) under white light (1, 1, 1) -> coral.
    //          coral under red light  (1, 0, 0)   -> (1.0, 0.0, 0.0): only red survives.
    //          coral under green light(0, 1, 0)   -> (0.0, 0.5, 0.0): only green fraction.
    out_color = vec4(u_light_color * u_object_color, 1.0);
}

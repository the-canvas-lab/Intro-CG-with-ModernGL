#version 330 core

in vec3 in_position;
in vec3 in_normal;

// TODO: Declare an out vec3 (e.g. "out vec3 gouraud_color") to carry the
//       computed lighting result to the fragment shader.

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat3 normal_matrix;

uniform vec3 u_object_color;
uniform vec3 u_light_color;
uniform vec3 u_light_pos;
uniform vec3 u_view_pos;

void main() {
    vec4 world_pos = model * vec4(in_position, 1.0);
    gl_Position    = projection * view * world_pos;

    vec3 frag_pos = vec3(world_pos);
    vec3 norm     = normalize(normal_matrix * in_normal);

    // TODO: Compute ambient, diffuse, and specular using the same formulas
    //       as phong_object.frag (the left panel) — only the location changes.
    //       Store (ambient + diffuse + specular) * u_object_color into your
    //       out variable declared above.
    //
    // When done, watch both panels side by side: the right panel's specular
    // highlight will look banded at face edges because the colour is linearly
    // interpolated per triangle rather than recomputed per fragment.
}

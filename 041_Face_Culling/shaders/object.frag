#version 330 core

layout (location = 0) out vec4 out_color;

in vec2 tex_coords;
in float face_id;

uniform sampler2D u_texture;

// One blue tint per wall (indexed by the face_id vertex attribute), shaded
// like rough ambient occlusion - top brightest, bottom darkest - so the
// interior reads as a room with five distinguishable walls.
const vec3 INTERIOR_TINTS[5] = vec3[5](
    vec3(0.30, 0.50, 1.00),   // 0 back
    vec3(0.20, 0.36, 0.85),   // 1 left
    vec3(0.42, 0.60, 1.00),   // 2 right
    vec3(0.12, 0.22, 0.60),   // 3 bottom
    vec3(0.55, 0.72, 1.00)    // 4 top
);

void main() {
    // gl_FrontFacing is true when the fragment belongs to a front-facing
    // triangle (one whose vertices wind counter-clockwise as seen from the
    // camera). Back-facing fragments - the box interior - are coloured so
    // their presence or absence is obvious when switching cull modes.
    if (gl_FrontFacing) {
        out_color = texture(u_texture, tex_coords);
    } else {
        out_color = vec4(INTERIOR_TINTS[int(face_id + 0.5)], 1.0);
    }
}

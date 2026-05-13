#version 330 core

in vec3 in_position;

out vec3 v_color;

void main() {
    gl_Position = vec4(in_position, 1.0);

    // --- Vector construction -------------------------------------------------
    // A vec3 can be built from three floats, or by combining smaller vectors.
    vec2 xy = in_position.xy;           // swizzle: extract x and y as vec2
    vec3 full = vec3(xy, in_position.z); // construct vec3 from vec2 + float

    // --- Component access ----------------------------------------------------
    // Components are accessed with .x .y .z .w (position)
    // or equivalently  .r .g .b .a (color) — same underlying type, different names.
    float x = in_position.x;   // ranges from -0.5 to 0.5 for this triangle
    float y = in_position.y;

    // Remap x and y from [-0.5, 0.5] to [0.0, 1.0] for use as color channels.
    float r = x + 0.5;
    float g = y + 0.5;

    // --- Swizzling -----------------------------------------------------------
    // Components can be reordered or repeated freely.
    vec3 color = vec3(r, g, 0.5);   // R from x, G from y, B fixed
    v_color = color.rgb;            // .rgb is equivalent to .xyz — same vector
}

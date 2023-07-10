#version 400

#if defined VERTEX_SHADER

in vec2 in_vert;

in vec3 in_color;
out vec3 v_color;    // Goes to the fragment shader

void main() {
   gl_Position = vec4(in_vert, 0.0, 1.0);
   v_color = in_color;
}

#endif

#if defined FRAGMENT_SHADER

in vec3 v_color;
out vec4 f_color;

void main() {
    // We're not interested in changing the alpha value
    f_color = vec4(v_color, 1.0);
}

#endif
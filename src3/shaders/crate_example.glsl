#version 330

#if defined VERTEX_SHADER
uniform mat4 Mvp;

in vec3 in_position;
in vec3 in_normal;
in vec2 in_texcoord_0;

out vec3 v_vert;
out vec3 v_norm;

void main() {
    gl_Position = Mvp * vec4(in_position, 1.0);
    v_vert = in_position;
    v_norm = in_normal;
}

#elif defined FRAGMENT_SHADER

uniform vec3 Light;

in vec3 v_vert;
in vec3 v_norm;

out vec4 f_color;

void main() {
    float lum = clamp(dot(normalize(Light - v_vert), normalize(v_norm)), 0.0, 1.0) * 0.8 + 0.2;
    vec3 orange = vec3(1.0, 0.5, 0.0);  // RGB values for orange color
    f_color = vec4(orange * lum, 1.0);
}

#endif
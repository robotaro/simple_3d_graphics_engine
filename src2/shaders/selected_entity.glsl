#version 400

#if defined VERTEX_SHADER

in vec3 in_vert;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;
uniform mat4 model_matrix;

void main() {

    gl_Position = projection_matrix * view_matrix * model_matrix * vec4(in_vert, 1.0);
}
#endif

#if defined FRAGMENT_SHADER

layout(location=0) out vec4 out_selected_entity;

void main() {
    out_selected_entity = vec4(1.0, 0.0, 0.0, 1.0);
}

#endif

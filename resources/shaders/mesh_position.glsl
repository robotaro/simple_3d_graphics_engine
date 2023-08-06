#if defined VERTEX_SHADER

#version 400

in vec3 in_vert;
in vec3 in_normal;

out vec3 v_normal;
out vec3 v_position;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;
uniform mat4 model_matrix;

void main() {
    v_normal = in_normal;
    v_position = in_vert;
    gl_Position = projection_matrix * view_matrix * model_matrix * vec4(v_position, 1.0);
}

#elif defined FRAGMENT_SHADER

#endif
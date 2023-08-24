#version 400

#if defined VERTEX_SHADER

in vec3 in_vert;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;
uniform mat4 model_matrix;

void main() {
    vec3 world_position = (model_matrix * vec4(in_vert, 1.0)).xyz;
    gl_Position = projection_matrix * view_matrix * vec4(world_position, 1.0);

}
#endif

#if defined FRAGMENT_SHADER

layout(location=0) out vec4 out_selected_entity;

#include clipping.glsl

void main() {
    out_selected_entity = vec4(1.0, 0.0, 0.0, 1.0);
}

#endif

#if defined VERTEX_SHADER

#version 400

in vec3 in_position;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;
uniform mat4 model_matrix;

out vec3 v_position;

void main() {
    v_position = in_position;
    gl_Position = projection_matrix * view_matrix * model_matrix * vec4(v_position, 1.0);
}

#elif defined FRAGMENT_SHADER

#version 400

layout(location=0) out vec4 out_position;
layout(location=1) out vec4 out_obj_info;

in vec3 local_pos;
in vec4 pos;
flat in int instance_id;

int tri_id = gl_PrimitiveID;
uniform int object_id;

#include clipping.glsl

void main() {
    discard_if_clipped(local_pos);

    out_obj_info = vec4(object_id, tri_id, instance_id, 0.0);
    out_position = pos;
}

#endif
#version 400

#if defined VERTEX_SHADER

in vec3 in_vert;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;
uniform mat4 model_matrix;

out vec4 pos;
out vec3 local_pos;
flat out int instance_id;


void main() {

    vec3 world_position = (model_matrix * vec4(in_vert, 1.0)).xyz;

    gl_Position = projection_matrix * view_matrix * vec4(world_position, 1.0);
    instance_id = gl_InstanceID;

    pos = vec4(world_position, 1.0);
    local_pos = in_vert;
}
#endif

#if defined FRAGMENT_SHADER

layout(location=0) out vec4 out_position;
layout(location=1) out vec4 out_obj_info;

in vec3 local_pos;
in vec4 pos;
flat in int instance_id;

int tri_id = gl_PrimitiveID;
uniform int obj_id;

#include clipping.glsl

void main() {
    discard_if_clipped(local_pos);

    out_obj_info = vec4(obj_id, tri_id, instance_id, 0.0);
    out_position = pos;
}

#endif

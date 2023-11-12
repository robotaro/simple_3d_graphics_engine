#version 400

#if defined VERTEX_SHADER

in mat4 in_debug_transform;
out mat4 gs_transform;

void main() {
    gs_transform = in_debug_transform;
}

#elif defined GEOMETRY_SHADER

layout (points) in;
layout (points, max_vertices = 6) out;

in mat4 gs_transforms[];

uniform int mesh_type = 0;
uniform mat4 projection_matrix;
uniform mat4 view_matrix;

out vec3 v_color;


void main() {

    mat4 mvp = projection_matrix * inverse(view_matrix) * gs_transforms[gl_InvocationID];

    // X Axis (Red)
    gl_Position = mvp * vec4(0, 0, 0, 1);
    v_color = vec3(1.0, 0.0, 0.0);  // Red axis
    EmitVertex();

    gl_Position = mvp * vec4(1, 0, 0, 1);
    v_color = vec3(1.0, 0.0, 0.0);  // Red axis
    EmitVertex();

    // Y Axis (Green)
    gl_Position = mvp * vec4(0, 0, 0, 1);
    v_color = vec3(0.0, 1.0, 0.0);  // Red axis
    EmitVertex();

    gl_Position = mvp * vec4(0, 1, 0, 1);
    v_color = vec3(0.0, 1.0, 0.0);  // Red axis
    EmitVertex();

    // Z Axis (Blue)
    gl_Position = mvp * vec4(0, 0, 0, 1);
    v_color = vec3(0.0, 0.0, 1.0);  // Red axis
    EmitVertex();

    gl_Position = mvp * vec4(0, 0, 1, 1);
    v_color = vec3(1.0, 0.0, 0.0);  // Red axis
    EmitVertex();


    EndPrimitive();
}


#elif defined FRAGMENT_SHADER

uniform vec3 color = vec3(1.0, 1.0, 1.0);

in vec3 v_color;
out vec4 fragColor;

void main()
{
    fragColor = vec4(v_color, 1.0);
}

#endif

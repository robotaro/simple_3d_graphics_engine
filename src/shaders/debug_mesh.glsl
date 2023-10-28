#version 400

#if defined VERTEX_SHADER

in vec2 in_position;
in vec2 in_transform;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;
uniform mat4 model_matrix;
uniform int mesh_type = -1;

out vec3 gs_world_position;

void main() {
    gs_world_position = (projection_matrix * inverse(view_matrix) * model_matrix * vec4(v_local_position, 1.0)).xyz;
}


#elif defined GEOMETRY_SHADER

layout (points) in;
layout (lines, max_vertices = 6) out;

in vec3 gs_transforms[];

out vec2 fragColor;



void main() {

    vec3 transform = gs_transforms[0];


    mat4 modelViewProjection = projectionMatrix * viewMatrix * modelMatrix;
    gl_Position = modelViewProjection * transforms[gl_InvocationID] * gl_in[0].gl_Position;
    fragColor = vec3(1.0, 0.0, 0.0);  // Red axis
    EmitVertex();

    gl_Position = modelViewProjection * transforms[gl_InvocationID] * gl_in[0].gl_Position + vec4(0.0, 0.1, 0.0, 0.0);
    fragColor = vec3(0.0, 1.0, 0.0);  // Green axis
    EmitVertex();

    gl_Position = modelViewProjection * transforms[gl_InvocationID] * gl_in[0].gl_Position;
    fragColor = vec3(0.0, 0.0, 1.0);  // Blue axis
    EmitVertex();
    EndPrimitive();


    EndPrimitive();
}


#elif defined FRAGMENT_SHADER

uniform vec3 color = vec3(1.0, 1.0, 1.0);

out vec4 fragColor;

void main()
{
    float texture_color = texture(font_texture, uv).r;
    fragColor =  vec4(1.0, 1.0, 1.0, texture_color);
}

#endif

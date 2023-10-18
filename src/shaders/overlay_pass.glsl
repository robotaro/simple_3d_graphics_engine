#version 400

#if defined VERTEX_SHADER


in vec3 in_vert;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;
uniform mat4 model_matrix;

out vec3 v_local_position;
out vec3 v_world_position;
out vec3 v_view_position;


void main() {

    v_local_position = in_vert;
    v_world_position = (model_matrix * vec4(v_local_position, 1.0)).xyz;
    v_view_position = view_matrix[3].xyz;

    gl_Position = projection_matrix * inverse(view_matrix) * model_matrix * vec4(v_local_position, 1.0);
}

#elif defined FRAGMENT_SHADER

// Already defined in the vertex shader
struct Material {
    vec3 diffuse;
    vec3 ambient;
    vec3 specular;
    float shininess_factor;
    float metallic_factor;
    float roughness_factor;
};

uniform Material material = Material(
    vec3(0.85, 0.85, 0.85), // Default diffuse color (e.g., gray)
    vec3(1.0, 1.0, 1.0),    // Default ambient color
    vec3(1.0, 1.0, 1.0),    // Default specular color
    0.5,                    // Default shininess factor
    1.0,                    // Default metallic factor
    0.0                     // Default roughness factor
);

// Output buffers (Textures)
layout(location=0) out vec4 out_fragment_color;

// Input Buffers
in vec3 v_local_position;
in vec3 v_world_normal;
in vec3 v_view_position;
in vec3 v_world_position;

uniform mat4 model_matrix;

// MVP matrices
uniform mat4 view_matrix;

void main() {

    vec3 normal = normalize(v_world_normal);  // TODO: Consider not doint this per fragment. Assume normas ar unitary
    vec3 view_direction = normalize(v_view_position - v_world_position);

    vec3 color_rgb = material.diffuse;

    out_fragment_color = vec4(color_rgb, 1.0);

}


#endif
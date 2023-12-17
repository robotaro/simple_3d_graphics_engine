#version 400

#if defined VERTEX_SHADER

in vec3 in_vert;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;
uniform mat4 model_matrix;

void main() {
    // TODO: Remove inverse vie matrix and move to the CPU
    gl_Position = projection_matrix * view_matrix * model_matrix * vec4(in_vert, 1.0);
}

#elif defined FRAGMENT_SHADER

uniform vec3 color_diffuse;

// Output buffers (Textures)
layout(location=0) out vec4 out_fragment_color;

void main() {

    out_fragment_color = vec4(color_diffuse, 1.0);

}


#endif
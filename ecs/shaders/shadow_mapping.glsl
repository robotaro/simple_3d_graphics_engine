#version 400

#if defined VERTEX_SHADER

// Code modified from "Coder Space"

layout (location = 2) in vec3 in_position;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;
uniform mat4 model_matrix;

void main() {
    gl_Position = projection_matrix * view_matrix * model_matrix * vec4(in_position, 1.0);
}

#elif defined FRAGMENT_SHADER

void main() {
    // The main function is empty becayuse all we need is the depth function
}

#endif

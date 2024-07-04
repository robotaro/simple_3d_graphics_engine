#version 330

#if defined VERTEX_SHADER

uniform mat4 uViewProjMatrix;

layout(location = 0) in vec3 aPosition; // Position of the vertex
layout(location = 1) in vec4 aColor;    // Color of the vertex

out vec4 vColor; // Output color to the fragment shader

void main() {
    vColor = aColor; // Pass the color to the fragment shader
    gl_Position = uViewProjMatrix * vec4(aPosition, 1.0); // Transform the vertex position
}

#elif defined FRAGMENT_SHADER

in vec4 vColor; // Input color from the vertex shader

layout(location = 0) out vec4 fColor; // Output color of the fragment

void main() {
    fColor = vColor; // Set the fragment color
}
#endif

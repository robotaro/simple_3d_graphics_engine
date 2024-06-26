#version 430

layout (location = 0) in vec3 in_position;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

out vec3 frag_position;

void main() {
    vec4 world_position = m_model * vec4(in_position, 1.0);
    frag_position = world_position.xyz;
    gl_Position = m_proj * m_view * world_position;
}

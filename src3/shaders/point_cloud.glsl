#version 330

// Code modified from: https://github.com/StanislavPetrovV/3D-Number-Renderer-with-UMAP
#if defined VERTEX_SHADER

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_color;

out vec3 v_color;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

uniform bool u_constant_size = false;
uniform vec3 cam_pos;

void main() {
    float max_point_size = 100.0;
    float min_point_size = 10.0;
    float point_size = max_point_size;

    // Use the color provided by the attribute
    v_color = in_color;

    vec3 v_position = vec3(m_model * vec4(in_position, 1.0));

    if (!u_constant_size) {
        float dist = length(v_position - cam_pos);
        point_size = max(max_point_size / dist, min_point_size);
    }

    gl_PointSize = point_size;
    gl_Position = m_proj * m_view * vec4(v_position, 1);
}

#elif defined FRAGMENT_SHADER

layout (location = 0) out vec4 fragColor;

in vec3 v_color;

void main() {
    vec2 point_uv = 2.0 * gl_PointCoord - 1.0;

    float circle = smoothstep(1.0, 0.7, dot(point_uv, point_uv));
    if (circle < 0.1) discard;

    fragColor = vec4(vec3(circle * v_color), 1);
}

#endif
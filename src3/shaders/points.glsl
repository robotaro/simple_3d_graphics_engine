#version 430

// Code modified from: https://github.com/StanislavPetrovV/3D-Number-Renderer-with-UMAP

#if defined VERTEX_SHADER

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_color;

out vec3 v_color;

layout (std140, binding = 0) uniform UBO_MVP {
    mat4 m_proj;
    mat4 m_view;
    mat4 m_model;
    vec3 v_cam_pos;
    float padding_1;
};

uniform bool u_constant_size = true;

void main() {
    float max_point_size = 20.0;
    float min_point_size = 5.0;
    float point_size = max_point_size;

    // Use the color provided by the attribute
    v_color = in_color;

    vec3 v_position = vec3(m_model * vec4(in_position, 1.0));

    if (!u_constant_size) {
        float dist = length(v_position - v_cam_pos);
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
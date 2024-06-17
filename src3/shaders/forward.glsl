#version 430

#if defined VERTEX_SHADER

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec3 in_color;

out vec3 normal;
out vec3 color;
out vec3 fragPos;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_view_light;
uniform mat4 m_model;


void main() {
    fragPos = vec3(m_model * vec4(in_position, 1.0));
    normal = mat3(transpose(inverse(m_model))) * normalize(in_normal);
    color = in_color;
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}

#elif defined FRAGMENT_SHADER

layout (location = 0) out vec4 fragColor;

in vec3 normal;
in vec3 color;
in vec3 fragPos;

struct Light {
    vec3 position;
    vec3 Ia;
    vec3 Id;
    vec3 Is;
};

uniform Light light;
uniform vec3 camPos;

vec3 getLight(vec3 color) {
    vec3 Normal = normalize(normal);

    // ambient light
    vec3 ambient = light.Ia;

    // diffuse light
    vec3 lightDir = normalize(light.position - fragPos);
    float diff = max(0, dot(lightDir, Normal));
    vec3 diffuse = diff * light.Id;

    // specular light
    vec3 viewDir = normalize(camPos - fragPos);
    vec3 reflectDir = reflect(-lightDir, Normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0), 32);
    vec3 specular = spec * light.Is;

    return color * (ambient + (diffuse + specular));
}


void main() {
    float gamma = 2.2;
    vec3 final_color = pow(color, vec3(gamma));

    final_color = getLight(final_color);

    final_color = pow(final_color, 1 / vec3(gamma));
    fragColor = vec4(final_color, 1.0);
}

#endif
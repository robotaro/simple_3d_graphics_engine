#version 430

#if defined VERTEX_SHADER

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec3 in_color;

out vec3 normal;
out vec3 color;
out vec3 fragPos;

layout (std140) uniform UBO_MVP {
    mat4 m_proj;
    mat4 m_view;
    mat4 m_model;
};

uniform mat4 m_view_light;


void main() {
    fragPos = vec3(m_model * vec4(in_position, 1.0));
    normal = mat3(transpose(inverse(m_model))) * normalize(in_normal);
    color = in_color;
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}

#elif defined FRAGMENT_SHADER

layout (location = 0) out vec4 out_fragColor;
layout (location = 1) out vec4 out_fragment_entity_info;

in vec3 normal;
in vec3 color;
in vec3 fragPos;

struct Light {
    vec3 position;
    vec3 Ia;
    vec3 Id;
    vec3 Is;
};

uniform int entity_id;  // You write to this uniform the ID of the entity being rendered
uniform Light light;
uniform vec3 camPos;
uniform bool hash_color = false;  // Add this uniform

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

// MurmurHash3 32-bit finalizer.
uint hash(uint h) {
    h ^= h >> 16;
    h *= 0x85ebca6bu;
    h ^= h >> 13;
    h *= 0xc2b2ae35u;
    h ^= h >> 16;
    return h;
}

// Hash an int value and return a color.
vec3 int_to_color(uint i) {
    uint h = hash(i);

    vec3 c = vec3(
        (h >>  0u) & 255u,
        (h >>  8u) & 255u,
        (h >> 16u) & 255u
    );

    return c * (1.0 / 255.0);
}

void main() {
    if (hash_color) {
        // Debug output colors
        vec3 hashed_color = int_to_color(uint(entity_id));
        out_fragColor = vec4(hashed_color, 1.0);
    } else {
        float gamma = 2.2;
        vec3 final_color = pow(color, vec3(gamma));

        final_color = getLight(final_color);

        final_color = pow(final_color, 1 / vec3(gamma));

        // Write to output textures
        out_fragColor = vec4(final_color, 1.0);
    }

    out_fragment_entity_info = vec4(entity_id, 0, 0, 1);  // Always write entity ID to the info texture
}

#endif
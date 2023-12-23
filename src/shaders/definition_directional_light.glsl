struct DirectionalLight {
    vec3 direction;
    float strength;
    vec3 diffuse;
    float padding_0;
    vec3 specular;
    float padding_1;
    mat4 matrix;
    bool shadow_enabled;
    bool enabled;
};

layout (std140, binding = 2) uniform DirectionalLightBlock {
    DirectionalLight directional_light[4];
} ubo_directional_lights;
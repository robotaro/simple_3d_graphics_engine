struct PointLight {
    vec3 position;
    float padding_0;
    vec3 diffuse;
    float intensity;
    vec3 specular;
    float enabled;
    vec3 attenuation_coeffs;
    float padding_1;
};

layout (std140, binding = 1) uniform PointLightBlock {
    PointLight point_light[8];
} ubo_point_lights;
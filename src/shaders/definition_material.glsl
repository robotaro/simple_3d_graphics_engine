struct Material {
    vec3 diffuse;
    int color_source;
    vec3 diffuse_highlight;
    int lighting_mode;
    vec3 specular;
    float padding_0;
    float shininess_factor;
    float metallic_factor;
    float roughness_factor;
    float padding_1;
};

layout (std140, binding = 0) uniform MaterialBlock {
    Material material[32];
} ubo_materials;
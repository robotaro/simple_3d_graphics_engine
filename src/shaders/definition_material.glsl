struct Material {
    vec3 diffuse;
    float padding00;
    vec3 ambient;
    float padding01;
    vec3 specular;
    float padding02;
    float shininess_factor;
    float metallic_factor;
    float roughness_factor;
    float padding03;
};
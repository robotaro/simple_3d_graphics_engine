struct PointLight {
    vec3 position;
    vec3 diffuse;
    vec3 specular;
    vec3 attenuation_coeffs;
    float intensity;
    bool enabled;
};
struct DirectionalLight {
    vec3 direction;
    vec3 diffuse;
    vec3 specular;
    float strength;
    mat4 matrix;
    bool shadow_enabled;
    bool enabled;
};
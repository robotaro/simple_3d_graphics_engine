struct SpotLight {
    vec3 color;
    float intensity;
    float range;
    vec3 position;
    vec3 direction;
    float light_angle_scale;
    float light_angle_offset;

    #ifdef SPOT_LIGHT_SHADOWS
    sampler2D shadow_map;
    mat4 light_matrix;
    #endif
};

struct DirectionalLight {
    vec3 color;
    float intensity;
    vec3 direction;

    #ifdef DIRECTIONAL_LIGHT_SHADOWS
    sampler2D shadow_map;
    mat4 light_matrix;
    #endif
};

struct PointLight {
    vec3 color;
    float intensity;
    float range;
    vec3 position;

    #ifdef POINT_LIGHT_SHADOWS
    samplerCube shadow_map;
    #endif
};
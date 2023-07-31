// NOTE: The following variables also need to be set from outside
//       - MAX_DIRECTIONAL_LIGHTS
//       - MAX_SPOT_LIGHTS
//       - MAX_POINT_LIGHTS


// ===================================================================
//                        Ambient Light (Global)
// ===================================================================

uniform float diffuse_coeff;
uniform vec3 ambient_light;
uniform float ambient_coeff;

// ===================================================================
//                      Directional Light
// ===================================================================

struct DirectionalLight {
    vec3 color;
    float intensity;  // or strength
    vec3 direction;
    bool shadow_enabled;
    mat4 matrix;

    #ifdef DIRECTIONAL_LIGHT_SHADOWS
    sampler2D shadow_map;
    mat4 light_matrix;
    #endif
};

uniform int num_directional_lights;
uniform DirectionalLight directional_lights[MAX_DIRECTIONAL_LIGHTS];

// Gratefully adopted from https://learnopengl.com/Advanced-Lighting/Shadows/Shadow-Mapping
float shadow_calculation(sampler2DShadow shadow_map, vec4 frag_pos_light_space, vec3 light_dir, vec3 normal) {
    // perform perspective divide (not needed for orthographic projection)
    vec3 projCoords = frag_pos_light_space.xyz / frag_pos_light_space.w;

    // transform to [0,1] range
    projCoords = projCoords * 0.5 + 0.5;

    // get closest depth value from light's perspective (using [0,1] range fragPosLight as coords)
    // float closestDepth = texture(shadow_map, projCoords.xy).r;

    // get depth of current fragment from light's perspective
    float currentDepth = projCoords.z;

    // calculate bias to remove shadow acne
    float bias = max(0.0005 * (1.0 - dot(normal, light_dir)), 0.001);

    float shadow = 0.0;
    vec2 texelSize = 1.0 / textureSize(shadow_map, 0);
    for(int x = -1; x <= 1; ++x) {
        for(int y = -1; y <= 1; ++y) {
             shadow += texture(shadow_map, vec3(projCoords.xy + vec2(x, y) * texelSize, currentDepth - bias));
        }
    }
    shadow /= 9.0;

    if (projCoords.z > 1.0)
        shadow = 0.0;

    return shadow;
}

vec3 directional_light(DirLight dir_light, vec3 color, vec3 fragPos, vec3 normal, float shadow) {
    vec3 lightDir = -dir_light.direction;
    float diff = max(dot(normal, lightDir), 0.0);
    vec3 diffuse = diffuse_coeff * diff * dir_light.color * dir_light.intensity;
    return (1.0 - shadow) * diffuse * color;
}

vec3 compute_lighting(vec3 vertex, vec3 normal, vec3 base_color,  vec4 vert_light[NR_DIR_LIGHTS]) {
    vec3 color = vec3(0.0, 0.0, 0.0);
    for(int i = 0; i < NR_DIR_LIGHTS; i++){
        float shadow = dirLights[i].shadow_enabled ? shadow_calculation(shadow_maps[i], vert_light[i], -dirLights[i].direction, normal) : 0.0;
        color += directional_light(dirLights[i], base_color.rgb, vertex, normal, shadow);
    }
    color += ambient_strength * ambient_coeff * base_color;
    return color;
}

// ===================================================================
//                      Spot Light
// ===================================================================

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

uniform SpotLight spot_lights[MAX_SPOT_LIGHTS];
uniform int num_spot_lights;


// ===================================================================
//                        Point Light
// ===================================================================

struct PointLight {
    vec3 color;
    float intensity;
    float range;
    vec3 position;

    #ifdef POINT_LIGHT_SHADOWS
    samplerCube shadow_map;
    #endif
};

uniform PointLight point_lights[MAX_POINT_LIGHTS];
uniform int num_point_lights;
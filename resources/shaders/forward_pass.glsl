#version 400

#if defined VERTEX_SHADER

struct Material {
    vec3 diffuse;
    vec3 ambient;
    vec3 specular;
    float shininess_factor;
    float metallic_factor;
    float roughness_factor;
};

struct GlobalAmbient
{
    vec3 direction;  // direction of top color
    vec3 top;        // top color
    vec3 bottom;     // bottom color
    float strength;
};

in vec3 in_vert;
in vec3 in_normal;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;
uniform mat4 model_matrix;
uniform mat4 dir_light_view_matrix;

uniform GlobalAmbient global = GlobalAmbient(
    vec3(0.0, 1.0, 0.0),
    vec3(1.0, 1.0, 1.0),
    vec3(0.0, 0.0, 0.0),
    1.0
);

uniform Material material = Material(
    vec3(0.85, 0.85, 0.85), // Default diffuse color (e.g., gray)
    vec3(1.0, 1.0, 1.0),    // Default ambient color
    vec3(1.0, 1.0, 1.0),    // Default specular color
    0.5,                    // Default shininess factor
    1.0,                    // Default metallic factor
    0.0                     // Default roughness factor
);

uniform vec3 hemisphere_up_color = vec3(1.0, 1.0, 1.0);
uniform vec3 hemisphere_down_color = vec3(0.0, 0.0, 0.0);
uniform vec3 hemisphere_light_direction = vec3(0.0, 1.0, 0.0);

out vec3 v_local_position;
out vec3 v_world_normal;
out vec3 v_world_position;
out vec3 v_view_position;
out vec3 v_ambient_color;
out Material v_material;

void main() {

    v_local_position = in_vert;
    v_world_position = (model_matrix * vec4(v_local_position, 1.0)).xyz;
    v_world_normal = mat3(transpose(inverse(model_matrix))) * in_normal;  // World normal
    v_view_position = view_matrix[3].xyz;

    //Make sure global ambient direction is unit length
    vec3 hemisphere_light_direction = normalize(hemisphere_light_direction);

    //Calculate cosine of angle between global ambient direction and normal
    float cos_theta = dot(hemisphere_light_direction, v_world_normal);

    //Calculate global ambient colour
    float alpha = 0.5 + (0.5 * cos_theta);
    v_ambient_color = alpha * global.top * material.diffuse + (1.0 - alpha) * global.bottom * material.diffuse;

    v_material = material;

    gl_Position = projection_matrix * inverse(view_matrix) * model_matrix * vec4(v_local_position, 1.0);;
}

#elif defined FRAGMENT_SHADER

#define MAX_DIRECTIONAL_LIGHTS 4
#define MAX_POINT_LIGHTS 8

// Already defined in the vertex shader
struct Material {
    vec3 diffuse;
    vec3 ambient;
    vec3 specular;
    float shininess_factor;
    float metallic_factor;
    float roughness_factor;
};

struct PointLight {
    vec3 position;
    vec3 diffuse;
    vec3 specular;
    vec3 attenuation_coeffs;
    float intensity;
    bool enabled;
};

struct DirectionalLight {
    vec3 direction;
    vec3 diffuse;
    vec3 specular;
    float strength;
    mat4 orthogonal_matrix;
    bool shadow_enabled;
    bool enabled;
};

// Output buffers (Textures)
layout(location=0) out vec4 out_fragment_color;
layout(location=1) out vec4 out_fragment_normal;
layout(location=2) out vec4 out_fragment_world_position;
layout(location=3) out vec4 out_fragment_entity_info;

// Input Buffers
in vec3 v_local_position;
in vec3 v_world_normal;
in vec3 v_view_position;
in vec3 v_world_position;
in vec3 v_ambient_color;
in Material v_material;

// Entity details
uniform int entity_id;
uniform int entity_render_mode;

// Rendering Mode details
uniform bool ambient_hemisphere_light_enabled = true;
uniform bool point_lights_enabled = true;
uniform bool directional_lights_enabled = true;
uniform bool gamma_correction_enabled = true;
uniform bool shadow_enabled = true;

uniform mat4 model_matrix;
uniform bool temp_flag = true;

uniform float gamma = 2.2;

// MVP matrices
uniform mat4 view_matrix;

// Lights
uniform int num_point_lights = 0;
uniform int num_directional_lights = 0;

uniform PointLight point_lights[MAX_POINT_LIGHTS];
uniform DirectionalLight directional_lights[MAX_DIRECTIONAL_LIGHTS];
uniform sampler2DShadow shadow_depth_texture;

vec3 calculate_directional_light(DirectionalLight light, vec3 normal, vec3 viewDir, float shadow_coeff);
vec3 calculate_point_light(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir);
float shadow_calculation(sampler2DShadow shadow_map, vec4 frag_pos_light_space, vec3 light_dir, vec3 normal);

void main() {

    vec3 normal = normalize(v_world_normal);  // TODO: Consider not doint this per fragment. Assume normas ar unitary
    vec3 view_direction = normalize(v_view_position - v_world_position);

    vec3 color_rgb = vec3(0.0);

    // Ambient Lighting
    if (ambient_hemisphere_light_enabled)
        color_rgb += v_ambient_color;

    // Point lights
    if (point_lights_enabled)
        for(int i = 0; i < num_point_lights; i++)
        {
            if(!point_lights[i].enabled) continue;
            color_rgb += calculate_point_light(point_lights[i], normal, v_world_position, view_direction);
        }

    // Directional lighting
    if (directional_lights_enabled)
        for(int i = 0; i < num_directional_lights; i++)
        {
            if (!directional_lights[i].enabled) continue;

            float shadow_coeff = shadow_calculation(shadow_depth_texture, vec4(1.0), vec3(1.0), v_world_normal);

            color_rgb += calculate_directional_light(directional_lights[i], normal, view_direction, shadow_coeff);
        }

    // Gamma correction
    if (gamma_correction_enabled)
        color_rgb = pow(color_rgb, vec3(1.0 / gamma));

    out_fragment_color = vec4(color_rgb, 1.0);
    out_fragment_normal = vec4(normal, 1.0);
    out_fragment_world_position = vec4(v_world_position, 1);
    out_fragment_entity_info = vec4(entity_id, 0, 0, 1);
}

vec3 calculate_directional_light(DirectionalLight light, vec3 normal, vec3 viewDir, float shadow_coeff)
{
    vec3 lightDir = normalize(light.direction);

    // diffuse shading
    float diff = max(dot(normal, lightDir), 0.0);

    // specular shading
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), v_material.shininess_factor);

    // Combine results
    vec3 diffuse  = light.diffuse * diff * v_material.diffuse;
    vec3 specular = light.specular * spec * v_material.specular;

    return (1.0 - shadow_coeff) * (diffuse + specular);
}

vec3 calculate_point_light(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir)
{
    // Direction
    vec3 lightDir = normalize(light.position - fragPos);

    // diffuse shading
    float diff = max(dot(normal, lightDir), 0.0);

    // specular shading
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), v_material.shininess_factor);

    // attenuation
    float distance    = length(light.position - fragPos);
    float attenuation = 1.0 / (light.attenuation_coeffs.r +
                               light.attenuation_coeffs.g * distance +
                               light.attenuation_coeffs.b * (distance * distance));

    // combine results
    vec3 diffuse  = light.diffuse  * diff * v_material.diffuse;
    vec3 specular = light.specular * spec * v_material.specular;
    diffuse  *= attenuation;
    specular *= attenuation;
    return  diffuse + specular;
}

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


/*
float get_soft_shadow_x16() {
    float shadow;
    float swidth = 1.0;
    float endp = swidth * 1.5;
    for (float y = -endp; y <= endp; y += swidth) {
        for (float x = -endp; x <= endp; x += swidth) {
            shadow += lookup(x, y);
        }
    }
    return shadow / 16.0;
}
*/
#endif
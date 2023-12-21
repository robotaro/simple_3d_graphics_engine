#version 430

//================================================[ Vertex Shader ]=====================================================

#if defined VERTEX_SHADER

#define RENDER_MODE_COLOR_SOURCE_SINGLE 0
#define RENDER_MODE_COLOR_SOURCE_BUFFER 1
#define RENDER_MODE_COLOR_SOURCE_UV 2

#define MAX_MATERIALS 32
#define MAX_TRANSFORMS 128

#include definition_material.glsl

struct GlobalAmbient
{
    vec3 direction;  // direction of top color
    vec3 top;        // top color
    vec3 bottom;     // bottom color
    float strength;
};

// Input VBOs
in vec3 in_vert;
in vec3 in_normal;
in vec3 in_color;

layout (std140, binding = 0) uniform MaterialBlock {
    Material material[MAX_MATERIALS];
} ubo_materials;

layout (std140, binding = 3) uniform TransformBlock {
    mat4 transforms[MAX_TRANSFORMS];
}ubo_transforms;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;
uniform mat4 dir_light_view_matrix;

uniform vec3 camera_position;
uniform int material_index = 0;

uniform GlobalAmbient global = GlobalAmbient(
    vec3(0.0, 1.0, 0.0),
    vec3(1.0, 1.0, 1.0),
    vec3(0.0, 0.0, 0.0),
    1.0
);

uniform vec3 hemisphere_up_color = vec3(1.0, 1.0, 1.0);
uniform vec3 hemisphere_down_color = vec3(0.0, 0.0, 0.0);
uniform vec3 hemisphere_light_direction = vec3(0.0, 1.0, 0.0);

out vec3 v_local_position;
out vec3 v_world_normal;
out vec3 v_world_position;
out vec3 v_camera_position;
out vec3 v_ambient_color;
flat out int v_instance_id;

void main() {

    mat4 model_matrix = ubo_transforms.transforms[gl_InstanceID];

    v_instance_id = gl_InstanceID;
    v_local_position = in_vert;
    v_world_position = (model_matrix * vec4(v_local_position, 1.0)).xyz;
    v_world_normal = mat3(transpose(inverse(model_matrix))) * in_normal;  // TODO: Check if this is correct
    v_camera_position = camera_position;

    Material material = ubo_materials.material[material_index];

    // Make sure global ambient direction is unit length
    vec3 hemisphere_light_direction = normalize(hemisphere_light_direction);

    // Calculate cosine of angle between global ambient direction and normal
    float cos_theta = dot(hemisphere_light_direction, v_world_normal);

    vec3 base_color = vec3(0.0);
    if (material.color_source == 0){
        base_color = ubo_materials.material[material_index].diffuse;
    } else if(material.color_source == 1) {
        base_color = in_color;
    }

    // Calculate global ambient colour
    float alpha = 0.5 + (0.5 * cos_theta);
    v_ambient_color = alpha * global.top * base_color + (1.0 - alpha) * global.bottom * base_color;

    gl_Position = projection_matrix * view_matrix * model_matrix * vec4(v_local_position, 1.0);
}
//===============================================[ Fragment Shader ]====================================================
#elif defined FRAGMENT_SHADER

#define MAX_MATERIALS 32
#define MAX_POINT_LIGHTS 8
#define MAX_DIRECTIONAL_LIGHTS 4

#include definition_material.glsl
#include definition_point_light.glsl
#include definition_directional_light.glsl

// Output buffers (Textures)
layout(location=0) out vec4 out_fragment_color;
layout(location=1) out vec4 out_fragment_normal;
layout(location=2) out vec4 out_fragment_world_position;
layout(location=3) out vec4 out_fragment_entity_info;

// Input Buffers
in vec3 v_local_position;
in vec3 v_world_normal;
in vec3 v_camera_position;
in vec3 v_world_position;
in vec3 v_ambient_color;
flat in int v_instance_id;

layout (std140, binding = 0) uniform MaterialBlock {
    Material material[MAX_MATERIALS];
} ubo_materials;

layout (std140, binding = 1) uniform PointLightBlock {
    PointLight point_light[MAX_POINT_LIGHTS];
} ubo_point_lights;

// Entity details
uniform int entity_id;
uniform int entity_render_mode;

// Rendering Mode details
uniform bool ambient_hemisphere_light_enabled = true;
uniform bool point_lights_enabled = true;
uniform bool directional_lights_enabled = true;
uniform bool gamma_correction_enabled = true;
uniform bool shadows_enabled = false;
uniform int  material_index = 0;
uniform mat4 model_matrix;

uniform float gamma = 2.2;

// MVP matrices
uniform mat4 view_matrix;

// Lights
uniform int num_directional_lights = 0;

uniform DirectionalLight directional_lights[MAX_DIRECTIONAL_LIGHTS];
uniform sampler2D shadow_maps[MAX_DIRECTIONAL_LIGHTS]; // Assuming one shadow map per light

vec3 calculate_directional_light(DirectionalLight light, Material material, vec3 material_color, vec3 normal, vec3 viewDir);
vec3 calculate_point_light(PointLight light, Material material, vec3 normal, vec3 material_color, vec3 fragPos, vec3 viewDir);
float shadow_calculation(mat4 light_view_projection_matrix, sampler2D shadow_map, float normal);

void main() {

    Material material = ubo_materials.material[material_index];
    vec3 normal = normalize(v_world_normal);  // TODO: Consider not doint this per fragment. Assume normas ar unitary
    vec3 view_direction = normalize(v_camera_position - v_world_position);
    vec3 color_rgb = vec3(0.0);

    vec3 base_color = vec3(0.0);
    if (material.color_source == 0){
        base_color = material.diffuse;
    }

    if (material.lighting_mode == 0){
        color_rgb = base_color;
    }

    // Ambient Lighting
    if (ambient_hemisphere_light_enabled && material.lighting_mode == 1)
        color_rgb += v_ambient_color;

    // Point lights
    if (point_lights_enabled && material.lighting_mode == 1)
        for(int i = 0; i < MAX_POINT_LIGHTS; i++)
        {
            if(ubo_point_lights.point_light[i].enabled == 0.0) continue;

            color_rgb += calculate_point_light(
                ubo_point_lights.point_light[i],
                material,
                base_color,
                normal,
                v_world_position,
                view_direction);
        }

    // Directional lighting
    if (directional_lights_enabled && material.lighting_mode == 1)
        for(int i = 0; i < num_directional_lights; i++)
        {
            if (!directional_lights[i].enabled) continue;

            // Light
            vec3 dir_light = calculate_directional_light(directional_lights[i], material, base_color, normal, view_direction);

            // Shadow
            if (shadows_enabled)
            {
                // Shadows are disabled for now
                float nl = clamp(dot(normal, directional_lights[i].direction), 0.0, 1.0);
                float shadow = shadow_calculation(
                    directional_lights[i].matrix,
                    shadow_maps[i],
                    nl);

                shadow = clamp(shadow, 0.0, 1.0);
                dir_light *= (1.0 - shadow);
            }

            color_rgb += dir_light;
        }

    // Gamma correction
    if (gamma_correction_enabled && material.lighting_mode == 1)
        color_rgb = pow(color_rgb, vec3(1.0 / gamma));

    out_fragment_color = vec4(color_rgb, 1.0);
    out_fragment_normal = vec4(normal, 1.0);
    out_fragment_world_position = vec4(v_world_position, 1);
    out_fragment_entity_info = vec4(entity_id, v_instance_id, 0, 1);
}

vec3 calculate_directional_light(DirectionalLight light, Material material, vec3 material_color, vec3 normal, vec3 viewDir)
{
    vec3 lightDir = normalize(-light.direction);

    // diffuse shading
    float diff = max(dot(normal, lightDir), 0.0);

    // specular shading
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess_factor);

    // Combine results
    vec3 diffuse  = light.diffuse * diff * material_color;
    vec3 specular = light.specular * spec * material.specular;

    return diffuse + specular;
}

vec3 calculate_point_light(PointLight light, Material material, vec3 material_color, vec3 normal, vec3 fragPos, vec3 viewDir)
{
    // Direction
    vec3 lightDir = normalize(light.position - fragPos);

    // diffuse shading
    float diff = max(dot(normal, lightDir), 0.0);

    // specular shading
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess_factor);

    // attenuation
    float distance    = length(light.position - fragPos);
    float attenuation = 1.0 / (light.attenuation_coeffs.r +
                               light.attenuation_coeffs.g * distance +
                               light.attenuation_coeffs.b * (distance * distance));

    // combine results
    vec3 diffuse  = light.diffuse  * diff * material_color;
    vec3 specular = light.specular * spec * material.specular;
    diffuse  *= attenuation;
    specular *= attenuation;
    return  diffuse + specular;
}

float texture2DCompare(sampler2D depths, vec2 uv, float compare) {
    return compare > texture(depths, uv.xy).r ? 1.0 : 0.0;
}

float texture2DShadowLerp(sampler2D depths, vec2 size, vec2 uv, float compare) {
    vec2 texelSize = vec2(1.0)/size;
    vec2 f = fract(uv*size+0.5);
    vec2 centroidUV = floor(uv*size+0.5)/size;

    float lb = texture2DCompare(depths, centroidUV+texelSize*vec2(0.0, 0.0), compare);
    float lt = texture2DCompare(depths, centroidUV+texelSize*vec2(0.0, 1.0), compare);
    float rb = texture2DCompare(depths, centroidUV+texelSize*vec2(1.0, 0.0), compare);
    float rt = texture2DCompare(depths, centroidUV+texelSize*vec2(1.0, 1.0), compare);
    float a = mix(lb, lt, f.y);
    float b = mix(rb, rt, f.y);
    float c = mix(a, b, f.x);
    return c;
}

float PCF(sampler2D depths, vec2 size, vec2 uv, float compare){
    float result = 0.0;
    for(int x=-1; x<=1; x++){
        for(int y=-1; y<=1; y++){
            vec2 off = vec2(x,y)/size;
            result += texture2DShadowLerp(depths, size, uv+off, compare);
        }
    }
    return result/9.0;
}

float shadow_calculation(mat4 light_view_projection_matrix, sampler2D shadow_map, float normal)
{
    // Shadow calculation for direction lights

    // Compute light texture UV coords
    vec4 proj_coords = vec4(light_view_projection_matrix * vec4(v_world_position.xyz, 1.0));
    vec3 light_coords = proj_coords.xyz / proj_coords.w;
    light_coords = light_coords * 0.5 + 0.5;
    float current_depth = light_coords.z;
    float bias = max(0.001 * (1.0 - normal), 0.0001) / proj_coords.w;
    float compare = (current_depth - bias);
    float shadow = PCF(shadow_map, textureSize(shadow_map, 0), light_coords.xy, compare);
    if (light_coords.z > 1.0) {
        shadow = 0.0;
    }
    return shadow;
}

/*
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
*/

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
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
};

in vec3 in_vert;
in vec3 in_normal;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;
uniform mat4 dir_light_view_matrix;
uniform mat4 model_matrix;

uniform GlobalAmbient global = GlobalAmbient(
    vec3(0.0, 1.0, 0.0),
    vec3(1.0, 1.0, 1.0),
    vec3(0.0, 0.0, 0.0)
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

out vec3 v_normal;
out vec3 v_position;
out vec3 v_viewpos;
out vec3 v_ambient_color;
out Material v_material;

void main() {

    v_position = in_vert;
    v_normal = in_normal;
    vec4 viewpos = inverse(view_matrix) * model_matrix * vec4(v_position, 1.0);
    v_viewpos = viewpos.xyz;

    //Make sure global ambient direction is unit length
    vec3 hemisphere_light_direction = normalize(hemisphere_light_direction);

    //Calculate cosine of angle between global ambient direction and normal
    float cos_theta = dot(hemisphere_light_direction, in_normal);

    //Calculate global ambient colour
    float alpha = 0.5 + (0.5 * cos_theta);
    v_ambient_color = alpha * global.top * material.diffuse + (1.0 - alpha) * global.bottom * material.diffuse;

    v_material = material;
    gl_Position = projection_matrix * viewpos;
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
    vec3 ambient;
    vec3 specular;
    vec3 attenuation_coeffs;
    float intensity;
};

struct DirectionalLight {
    vec3 direction;
    vec3 diffuse;
    vec3 ambient;
    vec3 specular;
    float strength;
    bool shadow_enabled;
    mat4 matrix;
};

// Output buffers (Textures)
layout(location=0) out vec4 out_fragment_color;
layout(location=1) out vec4 out_fragment_normal;
layout(location=2) out vec4 out_fragment_viewpos;
layout(location=3) out vec4 out_fragment_entity_info;

// Input Buffers
in vec3 v_normal;
in vec3 v_position;
in vec3 v_viewpos;
in vec3 v_ambient_color;
in Material v_material;

// Entity details
uniform int entity_id;
uniform int entity_render_mode;

// Rendering Mode details
uniform bool point_lights_enabled = true;
uniform bool directional_lights_enabled = true;
uniform bool gamma_correction_enabled = true;

uniform bool ambient_hemisphere_light_enabled = true;

uniform bool ambient_lighting_enabled = true;
uniform bool diffuse_lighting_enabled = true;
uniform bool specular_lighting_enabled = true;

uniform float gamma = 2.2;

// MVP matrices
uniform mat4 view_matrix;

// Lights
uniform int num_point_lights = 0;
uniform int num_directional_lights = 0;

uniform PointLight point_lights[MAX_POINT_LIGHTS];
uniform DirectionalLight directional_lights[MAX_DIRECTIONAL_LIGHTS];

// Functions pre-declaration
vec3 calculate_directional_light(DirectionalLight light, vec3 normal, vec3 viewDir);
vec3 calculate_point_light(PointLight light, vec3 normal, vec3 fragPos, vec3 viewDir);

void main() {

    vec3 view_position = transpose(inverse(view_matrix))[3].xyz;
    vec3 normal = normalize(v_normal);  // TODO: Consider not doint this per fragment. Assume normas ar unitary
    vec3 view_direction = normalize(view_position - v_position);


    vec3 color_rgb = vec3(0.0);

    if (ambient_hemisphere_light_enabled){
        color_rgb = v_ambient_color;
    }

    // Directional lighting
    if (directional_lights_enabled)
        for(int i = 0; i < num_directional_lights; i++)
            color_rgb += calculate_directional_light(directional_lights[i], normal, view_direction);

    // Point lights
    if (point_lights_enabled)
        for(int i = 0; i < num_point_lights; i++)
            color_rgb += calculate_point_light(point_lights[i], normal, v_position, view_direction);

    // Gamma correction
    if (gamma_correction_enabled)
        color_rgb = pow(color_rgb, vec3(1.0 / gamma));

    out_fragment_color = vec4(color_rgb, 1.0);
    out_fragment_normal = vec4(normal, 1.0);
    out_fragment_viewpos = vec4(v_viewpos, 1);
    out_fragment_entity_info = vec4(entity_id, 0, 0, 1);
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
    vec3 ambient  = vec3(0.0); //light.ambient  * v_material.diffuse;
    vec3 diffuse  = light.diffuse  * diff * v_material.diffuse;
    vec3 specular = light.specular * spec * v_material.specular;
    ambient  *= attenuation;
    diffuse  *= attenuation;
    specular *= attenuation;
    return (ambient + diffuse + specular);
}


vec3 calculate_directional_light(DirectionalLight light, vec3 normal, vec3 viewDir)
{
    vec3 lightDir = normalize(-light.direction);

    // diffuse shading
    float diff = max(dot(normal, lightDir), 0.0);

    // specular shading
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), v_material.shininess_factor);

    // Combine results
    vec3 ambient  = vec3(0.0); //light.ambient * v_material.diffuse;
    vec3 diffuse  = light.diffuse * diff * v_material.diffuse;
    vec3 specular = light.specular * spec * v_material.specular;
    return (ambient + diffuse + specular);
}


/*
vec3 calculate_point_lights_contribution(vec3 material_diffuse, vec3 material_specular){

    // ambient
    vec3 ambient = light.ambient * texture(material.diffuse, TexCoords).rgb;

    // diffuse
    vec3 norm = normalize(Normal);

    // vec3 lightDir = normalize(light.position - FragPos);
    vec3 lightDir = normalize(-light.direction);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = light.diffuse * diff * material_diffuse;

    // specular
    vec3 viewDir = normalize(viewPos - FragPos);
    vec3 reflectDir = reflect(-lightDir, norm);
    float specular = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    vec3 specular_color = light.specular * specular * material_specular;

    vec3 result = ambient + diffuse + specular_color;
    return result;
}*/


/*

vec3 add_light_and_shadow_contribution(vec3 color, vec3 normal) {

    vec3 Normal = normalize(normal);

    // ambient light
    vec3 ambient = light.Ia;

    // diffuse light
    vec3 lightDir = normalize(light.position - fragPos);
    float diff = max(0, dot(lightDir, Normal));
    vec3 diffuse = diff * light.Id;

    // specular light
    vec3 viewDir = normalize(camPos - fragPos);
    vec3 reflectDir = reflect(-lightDir, Normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0), 32);
    vec3 specular = spec * light.Is;

    // shadow
    float shadow = get_soft_shadow_x16();

    return color * (ambient + (diffuse + specular) * shadow);
}

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
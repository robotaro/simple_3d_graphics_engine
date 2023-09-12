#version 400

#if defined VERTEX_SHADER

in vec3 in_vert;
in vec3 in_normal;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;
uniform mat4 dir_light_view_matrix;
uniform mat4 model_matrix;

out vec3 v_normal;
out vec3 v_position;
out vec3 v_viewpos;

struct global_ambient
{
    vec3 direction;  // direction of top color
    vec3 top;        // top color
    vec3 bottom;     // bottom color
};


void main() {
    v_position = in_vert;
    v_normal = in_normal;
    vec4 viewpos = inverse(view_matrix) * model_matrix * vec4(v_position, 1.0);
    v_viewpos = viewpos.xyz;
    gl_Position = projection_matrix * viewpos;
}

#elif defined FRAGMENT_SHADER

#define MAX_DIRECTIONAL_LIGHTS 4
#define MAX_POINT_LIGHTS 8

struct PointLight {
    vec3 position;
    vec3 color;
};

struct DirectionalLight {
    vec3 direction;
    vec3 color;
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

// =======[ Uniforms ]========

// Entity details
uniform int entity_id;
uniform int entity_render_mode;

uniform float gamma = 2.2;

// MVP
uniform mat4 view_matrix;

// Material
uniform vec4 material_albedo = vec4(0.8, 0.8, 0.8, 1.0);
uniform float material_diffuse_factor = 0.5;
uniform float material_ambient_factor = 0.5;
uniform float material_specular_factor = 0.5;

// Old Light variables
const vec3 ambient = vec3(1.0);
uniform vec4 uColor = vec4(1.0, 0.5, 0.1, 1.0);
uniform float uHardness = 16.0;

// New Lights
uniform vec3 ambient_color = vec3(1.0, 1.0, 1.0);
uniform float ambient_strength;

uniform int num_point_lights = 0;
uniform PointLight point_lights[MAX_POINT_LIGHTS];

uniform int num_directional_lights = 0;
uniform DirectionalLight directional_lights[MAX_DIRECTIONAL_LIGHTS];


// Functions pre-declaration
//vec3 calculate_point_lights_contribution();
vec3 calculate_directional_light(DirectionalLight dir_light, vec3 color, vec3 normal);


void main() {

    vec3 view_position = transpose(inverse(view_matrix))[3].xyz;
    vec3 normal = normalize(v_normal);
    vec3 c = material_albedo.rgb * ambient;
    vec3 v = normalize(view_position - v_position);
    vec3 light_direction, r;
    float s, spec;

    vec3 color_rgb = material_albedo.rgb;

    // Calculate point light contributions
    for (int i = 0; i < num_point_lights; ++i){
        light_direction = normalize(point_lights[i].position - v_position);
        s = max(0.0, dot(normal, light_direction));
        color_rgb += color_rgb * s * point_lights[i].color;
        if (s > 0) {
            r = reflect(-light_direction, normal);
            spec = pow(max(0.0, dot(v, r)), uHardness);
            color_rgb += spec * point_lights[i].color;
        }
    }

    // Calculate directional light contributions
    for (int i = 0; i < num_directional_lights; ++i) {
        vec3 dir_light_color = calculate_directional_light(directional_lights[i], color_rgb, normal);
        color_rgb += dir_light_color;
    }

    // Apply gamma correction
    //color_rgb = pow(color_rgb, vec3(1.0 / gamma));


    out_fragment_color = vec4(color_rgb * 0.5, material_albedo.a);
    out_fragment_normal = vec4(normal, 1.0);
    out_fragment_viewpos = vec4(v_viewpos, 1);
    out_fragment_entity_info = vec4(entity_id, 0, 0, 1);
}


vec3 calculate_directional_light(DirectionalLight dir_light, vec3 color, vec3 normal) {
    vec3 light_direction = -dir_light.direction;
    float diff = max(dot(normal, light_direction), 0.0);
    vec3 diffuse = material_diffuse_factor * diff * dir_light.color * dir_light.strength;
    return diffuse * color;
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
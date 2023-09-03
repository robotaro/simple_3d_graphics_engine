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
    vec3 ambient_color;

    vec3 specular_color;
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

// MVP
uniform mat4 view_matrix;

// Material
uniform vec4 material_diffuse_color = vec4(0.8, 0.8, 0.8, 1.0);
uniform float material_ambient_factor = 0.5;
uniform float material_specular_factor = 0.5;

// Old Light variables
const vec3 lightpos0 = vec3(22.0, 16.0, 50.0);
const vec3 lightcolor0 = vec3(1.0, 1.0, 1.0);
const vec3 lightpos1 = vec3(-22.0, 8.0, -50.0);
const vec3 lightcolor1 = vec3(1.0, 1.0, 1.0);
const vec3 ambient = vec3(1.0);
uniform vec4 uColor = vec4(1.0, 0.5, 0.1, 1.0);
uniform float uHardness = 16.0;

// New Lights
uniform vec3 ambient_color = vec3(1.0, 1.0, 1.0);
uniform float ambient_strength;

uniform int num_point_lights = 0;
uniform PointLight point_Lights[MAX_POINT_LIGHTS];

uniform int num_directional_lights = 0;
uniform DirectionalLight directional_Lights[MAX_DIRECTIONAL_LIGHTS];


// Functions pre-declaration
vec3 calculate_point_lights_contribution();
vec3 calculate_directional_lights_contribution();


void main() {

    vec3 view_position = transpose(inverse(view_matrix))[3].xyz;
    vec3 normal = normalize(v_normal);
    vec3 c = material_diffuse_color.rgb * ambient;
    vec3 v = normalize(view_position - v_position);
    vec3 l, r;
    float s, spec;

    // DEBUG
    /*vec3 light_position = vec3(5, 5, 5);

    // ====== From LearnOpengl ===
    vec3 color = material_diffuse_color.rgb;

    // ambient contribution
    vec3 ambient_color = material_ambient_factor * color;

    // diffuse
    vec3 light_dir = normalize(light_position - v_position);
    vec3 normal = normalize(v_position);
    float diff = max(dot(light_dir, normal), 0.0);
    vec3 diffuse_color = diff * color;

    // specular
    vec3 view_dir = normalize(view_position - v_position);
    vec3 reflect_dir = reflect(-light_dir, normal);
    float specular_factor = 0.0;

    if(false)
    {
        vec3 halfwayDir = normalize(light_dir + view_dir);
        specular_factor = pow(max(dot(normal, halfwayDir), 0.0), 32.0);
    }
    else
    {
        vec3 reflectDir = reflect(-light_dir, normal);
        specular_factor = pow(max(dot(view_dir, reflectDir), 0.0), 8.0);
    }
    vec3 specular_color = vec3(0.3) * specular_factor; // assuming bright white light color
    out_fragment_color = vec4(ambient_color + diffuse_color + specular_color, material_diffuse_color.a);
    */

    l = normalize(lightpos0 - v_position);
    s = max(0.0, dot(normal, l));
    c += uColor.rgb * s * lightcolor0;
    if (s > 0) {
        r = reflect(-l, normal);
        spec = pow(max(0.0, dot(v, r)), uHardness);
        c += spec * lightcolor0;
    }

    l = normalize(lightpos1 - v_position);
    s = max(0.0, dot(normal, l));
    c += uColor.rgb * s * lightcolor1;
    if (s > 0) {
        r = reflect(-l, normal);
        spec = pow(max(0.0, dot(v, r)), uHardness);
        c += spec * lightcolor1;
    }

    out_fragment_color = vec4(c * 0.5, material_diffuse_color.a);
    out_fragment_normal = vec4(normal, 1.0);
    out_fragment_viewpos = vec4(v_viewpos, 1);
    out_fragment_entity_info = vec4(entity_id, 0, 0, 1);
}

vec3 calculate_point_lights_contribution(){

    vec3 light_value;
    /*
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
    //float shadow = getSoftShadowX16();
    float shadow = 1.0;

    return color * (ambient + (diffuse + specular) * shadow);
    */
    return light_value;

}

vec3 calculate_directional_lights_contribution(){
    vec3 light_value;
    return light_value;
}

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
#version 400

#if defined VERTEX_SHADER

in vec3 in_vert;
in vec3 in_normal;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;
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

// Output buffers (Textures)
layout(location=0) out vec4 out_fragment_color;
layout(location=1) out vec4 out_fragment_normal;
layout(location=2) out vec4 out_fragment_viewpos;
layout(location=3) out vec4 out_fragment_entity_info;

// Input Buffers
in vec3 v_normal;
in vec3 v_position;
in vec3 v_viewpos;

// Uniforms
uniform int entity_id;
uniform int selected_entity_id;
uniform mat4 view_matrix;
uniform vec4 uColor = vec4(1.0, 0.5, 0.1, 1.0);
uniform float uHardness = 16.0;

const vec3 lightpos0 = vec3(22.0, 16.0, 50.0);
const vec3 lightcolor0 = vec3(1.0, 0.95, 0.9);
const vec3 lightpos1 = vec3(-22.0, -8.0, -50.0);
const vec3 lightcolor1 = vec3(0.9, 0.95, 1.0);
const vec3 ambient = vec3(1.0);

void main() {

    vec3 view_position = inverse(view_matrix)[3].xyz;
    vec3 n = normalize(v_normal);
    vec3 c = uColor.rgb * ambient;
    vec3 v = normalize(view_position - v_position);
    vec3 l, r;
    float s, spec;

    l = normalize(lightpos0 - v_position);
    s = max(0.0, dot(n, l));
    c += uColor.rgb * s * lightcolor0;
    if (s > 0) {
        r = reflect(-l, n);
        spec = pow(max(0.0, dot(v, r)), uHardness);
        c += spec * lightcolor0;
    }

    l = normalize(lightpos1 - v_position);
    s = max(0.0, dot(n, l));
    c += uColor.rgb * s * lightcolor1;
    if (s > 0) {
        r = reflect(-l, n);
        spec = pow(max(0.0, dot(v, r)), uHardness);
        c += spec * lightcolor1;
    }

    out_fragment_color = vec4(c * 0.5, uColor.a);
    out_fragment_normal = vec4(n, 1.0);
    out_fragment_viewpos = vec4(v_viewpos, 1);
    out_fragment_entity_info = vec4(entity_id, 0, 0, 1);
}

#endif
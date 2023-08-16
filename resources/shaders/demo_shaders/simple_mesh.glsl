// Code from : https://github.com/eliemichel/Python3dViewer/tree/main/shaders
#if defined VERTEX_SHADER



#version 400

in vec3 in_vert;
in vec3 in_normal;

out vec3 v_normal;
out vec3 v_position;

uniform mat4 uPerspectiveMatrix;
uniform mat4 uViewMatrix;

void main() {
    v_normal = in_normal;
    v_position = in_vert;
    gl_Position = uPerspectiveMatrix * uViewMatrix * vec4(v_position, 1.0);
}

#elif defined FRAGMENT_SHADER

in vec3 v_normal;
in vec3 v_position;

out vec4 f_color;

uniform vec4 uColor = vec4(1.0, 0.5, 0.1, 1.0);
uniform mat4 uViewMatrix;
uniform float uHardness = 16.0;

const vec3 lightpos0 = vec3(22.0, 16.0, 50.0);
const vec3 lightcolor0 = vec3(1.0, 0.95, 0.9);
const vec3 lightpos1 = vec3(-22.0, -8.0, -50.0);
const vec3 lightcolor1 = vec3(0.9, 0.95, 1.0);
const vec3 ambient = vec3(1.0);

void main() {
    vec3 viewpos = inverse(uViewMatrix)[3].xyz;

    // This is a very basic lighting, for visualization only //

    vec3 n = normalize(v_normal);
    vec3 c = uColor.rgb * ambient;
    vec3 v = normalize(viewpos - v_position);
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

    f_color = vec4(c * 0.5, uColor.a);
}

#endif
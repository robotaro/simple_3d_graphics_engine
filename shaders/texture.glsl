#version 400

#if defined VERTEX_SHADER

in vec3 in_vertices;
in vec2 in_texcoord_0;
out vec2 uv0;

void main() {
    gl_Position = vec4(in_position, 1);
    uv0 = in_texcoord_0;
}

#elif defined FRAGMENT_SHADER

in vec2 uv0;
uniform sampler2D texture0;
out vec4 fragColor;

void main() {
    fragColor = texture(texture0, uv0);
}
#endif

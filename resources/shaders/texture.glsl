#version 400

#if defined VERTEX_SHADER

in vec3 in_position;
in vec2 in_uv;

out vec2 uv;

void main() {
    gl_Position = vec4(in_position, 1);
    uv = in_uv;
}

#elif defined FRAGMENT_SHADER

in vec2 uv;
uniform sampler2D texture0;
out vec4 fragColor;

void main() {
    fragColor = texture(texture0, uv);
}
#endif

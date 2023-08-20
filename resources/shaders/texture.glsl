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

#if defined COLOR_RGBA
    fragColor = texture(texture0, uv);

#elif defined COLOR_RGB
    fragColor = vec4(texture(texture0, uv));

#elif defined COLOR_FLOAT
    float value = texture(texture0, uv);
    fragColor = vec4(value, value, value, 1.0);

#elif defined COLOR_INT
    fragColor = texture(texture0, uv);

#else
    fragColor = texture(texture0, uv);  // RGBA by default
#endif
}
#endif

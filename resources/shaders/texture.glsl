#version 400

#if defined VERTEX_SHADER

in vec3 in_vert;
in vec2 in_uv;

out vec2 uv;

void main() {
    gl_Position = vec4(in_vert, 1);
    uv = in_uv;
}

#elif defined FRAGMENT_SHADER

// Input textures
uniform sampler2D color_texture;
uniform sampler2D normal_texture;

in vec2 uv;

uniform int selected_texture = 0;

out vec4 fragColor;

void main() {

    vec3 finalColor;

    if (selected_texture == 0) {
        // Display RGBA texture
        finalColor = texture(color_texture, uv).rgb;
    } else {
        // Display RGB texture
        finalColor = texture(normal_texture, uv).rgb;
    }

    fragColor = vec4(finalColor, 1.0);
}
#endif

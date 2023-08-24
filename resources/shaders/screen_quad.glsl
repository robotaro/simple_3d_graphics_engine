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
uniform sampler2D viewpos_texture;
uniform sampler2D entity_info_texture;
uniform sampler2D selected_entity_texture;

in vec2 uv;

uniform int selected_texture = 0;

out vec4 fragColor;

// MurmurHash3 32-bit finalizer.
uint hash(uint h) {
    h ^= h >> 16;
    h *= 0x85ebca6bu;
    h ^= h >> 13;
    h *= 0xc2b2ae35u;
    h ^= h >> 16;
    return h;
}

// Hash an int value and return a color.
vec3 int_to_color(uint i) {
    uint h = hash(i);

    vec3 c = vec3(
        (h >>  0u) & 255u,
        (h >>  8u) & 255u,
        (h >> 16u) & 255u
    );

    return c * (1.0 / 255.0);
}

void main() {

    vec3 finalColor;

    if (selected_texture == 0) {
        // Color
        finalColor = texture(color_texture, uv).rgb;
    } else if (selected_texture == 1) {
        // Normal
        finalColor = texture(normal_texture, uv).rgb;
    } else if (selected_texture == 2) {
        // Viewpos
        finalColor = texture(viewpos_texture, uv).xyz;
    } else if (selected_texture == 3) {
        // Entity ID
        uint id = floatBitsToUint(texture(entity_info_texture, uv).r);
        finalColor = int_to_color(id);
    } else if (selected_texture == 4) {
        // Instance ID
        uint id = floatBitsToUint(texture(entity_info_texture, uv).g);
        finalColor = int_to_color(id);
    } else if (selected_texture == 5) {
        // Current Selection
        finalColor = texture(selected_entity_texture, uv).rgb;

    }

    fragColor = vec4(finalColor, 1.0);
}
#endif

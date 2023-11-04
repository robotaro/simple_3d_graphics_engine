#version 400

#if defined VERTEX_SHADER

in vec2 in_position;
in vec2 in_size;
in vec2 in_uv_min;
in vec2 in_uv_max;

out vec2 gs_position;
out vec2 gs_size;
out vec2 gs_uv_min;
out vec2 gs_uv_max;

void main() {

    gs_position = in_position;
    gs_size = in_size;
    gs_uv_min = in_uv_min;
    gs_uv_max = in_uv_max;

    gl_Position = vec4(in_position, 0.0, 1.0);
}


#elif defined GEOMETRY_SHADER

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform mat4 projection_matrix; // Your projection matrix

// The inputs are expected to be arrays because you could be providing
// multiple points, like a line (2 points) and so on.
// The POINTS rendering mode means this is a 1-element array, hence
// the gs_position[0] :)

in vec2 gs_position[];
in vec2 gs_size[];
in vec2 gs_uv_min[];
in vec2 gs_uv_max[];

out vec2 uv;


void emitVertexWithUV(vec2 position, vec2 uvCoords) {
    gl_Position = projection_matrix * vec4(position, 0.0, 1.0);
    uv = uvCoords;
    EmitVertex();
}

void main() {

    // Calculate the rectangle vertex position
    vec2 position = gs_position[0].xy;

    // Emit the rectangle vertices with adjusted UV coordinates
    emitVertexWithUV(position, gs_uv_min[0]);
    emitVertexWithUV(position + vec2(0, gs_size[0].y), vec2(gs_uv_min[0].x, gs_uv_max[0].y));
    emitVertexWithUV(position + vec2(gs_size[0].x, 0), vec2(gs_uv_max[0].x, gs_uv_min[0].y));
    emitVertexWithUV(position + vec2(gs_size[0].x, gs_size[0].y), vec2(gs_uv_max[0].x, gs_uv_max[0].y));

    EndPrimitive();
}


#elif defined FRAGMENT_SHADER

uniform sampler2D font_texture;

in vec2 uv;

uniform vec3 font_color = vec3(1.0, 1.0, 1.0);

out vec4 fragColor;

void main()
{
    float texture_color = texture(font_texture, uv).r;
    fragColor =  vec4(1.0, 1.0, 1.0, texture_color);
}

#endif

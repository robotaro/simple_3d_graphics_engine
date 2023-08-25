#version 400

#if defined VERTEX_SHADER

in vec2 in_position;
in vec2 in_size;
in vec2 in_uv_position;
in vec2 in_uv_size;

out vec2 gs_position;
out vec2 gs_size;
out vec2 gs_uv_position;
out vec2 gs_uv_size;

void main() {

    gs_position = in_position;
    gs_size = in_size;
    gs_uv_position = in_uv_position;
    gs_uv_size = in_uv_size;

    gl_Position = vec4(in_position, 0.0, 1.0);
}


#elif defined GEOMETRY_SHADER

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

uniform mat4 projection_matrix; // Your projection matrix

// The inputs are expected to be arrays because you could prividing
// multiple points, like a line (2 points) and so on.
// The POINTS rendering mode means this is a 1-element array, hence
// the gs_position[0] :)

in vec2 gs_position[];
in vec2 gs_size[];
in vec2 gs_uv_position[];
in vec2 gs_uv_size[];

out vec2 uv;

void main() {
    // Calculate the rectangle vertices based on input data
    vec2 upperLeft = gs_position[0];
    vec2 lowerLeft = gs_position[0] + vec2(0, -gs_size[0].y);
    vec2 upperRight = gs_position[0] + gs_size[0];
    vec2 lowerRight = gs_position[0] + gs_size[0] + vec2(0, -gs_size[0].y);

    // Emit vertices for the rectangle
    gl_Position = projection_matrix * vec4(upperLeft, 0.0, 1.0);
    uv = gs_uv_position[0];
    EmitVertex();

    gl_Position = projection_matrix * vec4(lowerLeft, 0.0, 1.0);
    uv = gs_uv_position[0] + vec2(0.0, gs_uv_size[0].y);
    EmitVertex();

    gl_Position = projection_matrix * vec4(upperRight, 0.0, 1.0);
    uv = gs_uv_position[0] + vec2(gs_uv_size[0].x, 0.0);
    EmitVertex();

    gl_Position = projection_matrix * vec4(lowerRight, 0.0, 1.0);
    uv = gs_uv_position[0] + gs_uv_size[0];
    EmitVertex();

    EndPrimitive();
}


#elif defined FRAGMENT_SHADER

uniform sampler2DArray font_texture;

in vec2 uv;
flat in uint gs_char_id;

out vec4 fragColor;

void main()
{
    float texture_color = texture(font_texture, vec3(uv, gs_char_id)).r;
    fragColor =  vec4(texture_color, texture_color, texture_color, 1.0);
}
#endif

#version 400

#if defined VERTEX_SHADER

in float in_command_id;
in vec2 in_position;
in vec2 in_size;
in vec4 in_color;
in float in_edge_width;
in vec2 in_uv_min;
in vec2 in_uv_max;

out float gs_command_id;
out vec2 gs_position;
out vec2 gs_size;
out float gs_edge_width;
out vec4 gs_color;
out vec2 gs_uv_min;
out vec2 gs_uv_max;


flat out int command_id;


void main() {

    gs_command_id = in_command_id;
    gs_position = in_position;
    gs_size = in_size;
    gs_edge_width = in_edge_width;
    gs_color = in_color;
    gs_uv_min = in_uv_min;
    gs_uv_max = in_uv_max;

    gl_Position = vec4(in_position, 0.0, 1.0);
}


#elif defined GEOMETRY_SHADER

#include overlay_2d_constants.glsl

#define CIRCLE_NUM_SIDES 32


layout (points) in;
layout (triangle_strip, max_vertices=70) out;

uniform mat4 projection_matrix; // Your projection matrix

// The inputs are expected to be arrays because you could be providing
// multiple points, like a line (2 points) and so on.
// The POINTS rendering mode means this is a 1-element array, hence
// the gs_position[0] :)

in float gs_command_id[];
in vec2 gs_position[];
in vec2 gs_size[];
in float gs_edge_width[];
in vec4 gs_color[];
in vec2 gs_uv_min[];
in vec2 gs_uv_max[];


out float command_id_float;
out vec2 uv;
out vec4 geometry_color;

const float PI = 3.1415926535897932384626433832795;

void emitVertexWithUV(vec2 position, vec2 uvCoords) {
    gl_Position = projection_matrix * vec4(position, 0.0, 1.0);
    uv = uvCoords;
    EmitVertex();
}

void command_aabb_filled(vec2 position, vec2 size){
    vec2 fill_0 = position;
    vec2 fill_1 = vec2(position.x, position.y + size.y );
    vec2 fill_2 = vec2(position.x + size.x, position.y);
    vec2 fill_3 = vec2(position.x + size.x, position.y + size.y);

    geometry_color = gs_color[0].rgba;

    // Triangle A)
    gl_Position = projection_matrix * vec4(fill_0, 0.0, 1.0);
    EmitVertex();

    gl_Position = projection_matrix * vec4(fill_1, 0.0, 1.0);
    EmitVertex();

    gl_Position = projection_matrix * vec4(fill_2, 0.0, 1.0);
    EmitVertex();

    gl_Position = projection_matrix * vec4(fill_3, 0.0, 1.0);
    EmitVertex();
}

void command_aabb_edge(vec2 position, vec2 size, float edge){
    geometry_color = gs_color[0].rgba;

    gl_Position = projection_matrix * vec4(position, 0.0, 1.0);
    EmitVertex();

    gl_Position = projection_matrix * vec4(position.x + edge, position.y + edge, 0.0, 1.0);
    EmitVertex();

    gl_Position = projection_matrix * vec4(position.x + size.x, position.y, 0.0, 1.0);
    EmitVertex();

    gl_Position = projection_matrix * vec4(position.x + size.x - edge, position.y + edge, 0.0, 1.0);
    EmitVertex();

    gl_Position = projection_matrix * vec4(position.x + size.x , position.y + size.y, 0.0, 1.0);
    EmitVertex();

    gl_Position = projection_matrix * vec4(position.x + size.x - edge, position.y + size.y - edge, 0.0, 1.0);
    EmitVertex();

    gl_Position = projection_matrix * vec4(position.x, position.y + size.y, 0.0, 1.0);
    EmitVertex();

    gl_Position = projection_matrix * vec4(position.x + edge , position.y + size.y - edge, 0.0, 1.0);
    EmitVertex();

    gl_Position = projection_matrix * vec4(position, 0.0, 1.0);
    EmitVertex();

    gl_Position = projection_matrix * vec4(position.x + edge, position.y + edge, 0.0, 1.0);
    EmitVertex();
}

void command_character(vec2 position){
    emitVertexWithUV(position, gs_uv_min[0]);
    emitVertexWithUV(position + vec2(0, gs_size[0].y), vec2(gs_uv_min[0].x, gs_uv_max[0].y));
    emitVertexWithUV(position + vec2(gs_size[0].x, 0), vec2(gs_uv_max[0].x, gs_uv_min[0].y));
    emitVertexWithUV(position + vec2(gs_size[0].x, gs_size[0].y), vec2(gs_uv_max[0].x, gs_uv_max[0].y));
}

void command_aabb_textured(vec2 position){
    emitVertexWithUV(position, gs_uv_min[0]);
    emitVertexWithUV(position + vec2(0, gs_size[0].y), vec2(gs_uv_min[0].x, gs_uv_max[0].y));
    emitVertexWithUV(position + vec2(gs_size[0].x, 0), vec2(gs_uv_max[0].x, gs_uv_min[0].y));
    emitVertexWithUV(position + vec2(gs_size[0].x, gs_size[0].y), vec2(gs_uv_max[0].x, gs_uv_max[0].y));
}

void command_circle_edge(vec2 position, vec2 size, float edge){
    vec2 center = position;
    float radius = size.x; // Assuming size.x holds the radius value
    geometry_color = gs_color[0].rgba;

    float angle_step = (2.0 * PI) / float(CIRCLE_NUM_SIDES);
    float angle = 0.0;
    float half_edge = edge / 2.0;

    for (int i = 0; i < CIRCLE_NUM_SIDES + 1; ++i) {

        // Calculate the positions of the vertices
        vec2 offset_unit_vector = vec2(cos(angle), sin(angle));

        // Outer vertex of next segment
        vec2 outer_vertex = center + (radius + half_edge) * offset_unit_vector;
        gl_Position = projection_matrix * vec4(outer_vertex, 0.0, 1.0);
        EmitVertex();

        // Emmit outer vertex of this segment
        vec2 inner_vertex = center + (radius - half_edge) * offset_unit_vector;
        gl_Position = projection_matrix * vec4(inner_vertex, 0.0, 1.0);
        EmitVertex();

        // Update the angle for the next vertex
        angle += angle_step;
    }
}

void main() {

    // Easy to read variables
    vec2 position = gs_position[0].xy;
    vec2 size = gs_size[0].xy;
    float edge = gs_edge_width[0];
    command_id_float = gs_command_id[0];

    if (command_id_float == COMMAND_ID_AABB_FILLED) command_aabb_filled(position, size);
    else if (command_id_float == COMMAND_ID_AABB_EDGE) command_aabb_edge(position, size, edge);
    else if (command_id_float == COMMAND_ID_CHARACTER) command_character(position);
    else if (command_id_float == COMMAND_ID_AABB_TEXTURED) command_aabb_textured(position);
    else if (command_id_float == COMMAND_ID_CIRCLE_EDGE) command_circle_edge(position, size, edge);

    EndPrimitive();
}


#elif defined FRAGMENT_SHADER

#include overlay_2d_constants.glsl

uniform sampler2D font_texture;

// Four generic textures that you can bind and use
uniform sampler2D texture_0;
uniform sampler2D texture_1;
uniform sampler2D texture_2;
uniform sampler2D texture_3;

// uniform vec3 font_color = vec3(1.0, 1.0, 1.0);

in float command_id_float;
in vec2 uv;
in vec4 geometry_color;

out vec4 frag_color;


void main()
{

    if (command_id_float == COMMAND_ID_CHARACTER){
        float texture_color = texture(font_texture, uv).r;
        frag_color =  vec4(1.0, 1.0, 1.0, texture_color);

    } else {
        frag_color = geometry_color;

    }

}

#endif

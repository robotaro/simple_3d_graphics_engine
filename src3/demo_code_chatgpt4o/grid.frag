#version 430

layout (location = 0) out vec4 out_color;

in vec3 frag_position;

uniform vec3 grid_color;
uniform vec3 bg_color;
uniform vec3 x_axis_color;
uniform vec3 z_axis_color;
uniform float grid_spacing;
uniform float line_width;
uniform float fog_start;
uniform float fog_end;
uniform vec3 camera_pos;

void main() {
    // Calculate the distance from the fragment to the camera
    float distance_to_camera = length(frag_position - camera_pos);

    // Calculate the absolute world position
    float x = frag_position.x;
    float z = frag_position.z;

    // Calculate the distance to the nearest grid line
    float distance_to_x_line = abs(mod(x + grid_spacing / 2.0, grid_spacing) - grid_spacing / 2.0);
    float distance_to_z_line = abs(mod(z + grid_spacing / 2.0, grid_spacing) - grid_spacing / 2.0);

    // Determine the line width in world coordinates
    float half_line_width = line_width / 2.0;

    // Check if the fragment is on the X or Z axis
    bool is_on_x_axis = abs(z) < half_line_width;
    bool is_on_z_axis = abs(x) < half_line_width;

    // Check if the fragment is within the width of a grid line
    bool is_on_x_line = distance_to_x_line < half_line_width;
    bool is_on_z_line = distance_to_z_line < half_line_width;

    // Set the color based on whether the fragment is on a grid line or axis
    vec3 color = bg_color;
    if (is_on_x_axis) {
        color = x_axis_color; // Red for X axis
    } else if (is_on_z_axis) {
        color = z_axis_color; // Blue for Z axis
    } else if (is_on_x_line || is_on_z_line) {
        color = grid_color;
    }

    // Apply fog effect
    float fog_factor = clamp((distance_to_camera - fog_start) / (fog_end - fog_start), 0.0, 1.0);
    color = mix(color, bg_color, fog_factor);

    out_color = vec4(color, 1.0);
}
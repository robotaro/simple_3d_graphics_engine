#version 430

#if defined VERTEX_SHADER

//
// Picks a point from the depth buffer and returns the position in camera space, along with the object and triangle id
// Adapted from https://github.com/moderngl/moderngl-window/blob/master/examples/resources/programs/fragment_picking/picker.glsl
//

uniform sampler2D entity_info_texture;

uniform ivec2 texel_pos;

out int out_obj_id;
out int out_tri_id;
out int out_instance_id;

void main() {
    vec4 texel = texelFetch(entity_info_texture, texel_pos, 0);
    out_obj_id = int(texel.r);
    out_tri_id = int(texel.g);
    out_instance_id = int(texel.b);

    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);  // Set a dummy position
}

#endif
#version 400

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
    out_obj_id = int(texelFetch(entity_info_texture, texel_pos, 0).r);
    out_tri_id = int(texelFetch(entity_info_texture, texel_pos, 0).g);
    out_instance_id = int(texelFetch(entity_info_texture, texel_pos, 0).b);

    gl_Position = vec4(0.0, 0.0, 0.0, 1.0);  // Set a dummy position
}

#endif
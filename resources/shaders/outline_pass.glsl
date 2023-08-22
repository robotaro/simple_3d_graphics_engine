#version 400

#if defined VERTEX_SHADER

    in vec3 in_vert;

    void main() {
        gl_Position = vec4(in_vert, 1.0);
    }

#elif defined FRAGMENT_SHADER
    out vec4 fragColor;

    uniform vec3 outline_color;
    uniform sampler2D outline;

    void draw_selection_outline(int selected_mesh_id);

    void main() {
        // Transform pixel coordinates from float to int.
        ivec2 coords = ivec2(gl_FragCoord.xy);

        // Load the value at the current pixel.
        float v = texelFetch(outline, coords, 0).r;

        // If inside one of the objects to outline, discard.
        if(v > 0) {
            discard;
        }

        // Check if any of the neighbouring pixels is inside an object to outline.
        bool ok = false;
        for(int y = -1; y <= 1; y++) {
            for(int x = -1; x <= 1; x++) {
                if(y == 0 && x == 0) {
                    continue;
                }

                // Load a pixel at distance 2 and check if it's inside an object
                float v = texelFetch(outline, coords + ivec2(x, y) * 2, 0).r;
                if(v > 0) {
                    ok = true;
                }
            }
        }

        // If none of the pixels were inside discard
        if(!ok) {
            discard;
        }

        // Otherwise draw this pixel with the outline color
        fragColor = vec4(outline_color, 1.0);
    }

void draw_selection_outline(int selected_mesh_id){
    // Original code from : https://stackoverflow.com/questions/53897949/opengl-object-outline

    int thickness = 2;

    if (selected_mesh_id == 0){
        return;
    }

    int id = texture(texture_mesh_id, v_uv).r;

    if (id != selected_mesh_id && id != -1)
    {
        vec2 size = 1.0f / textureSize(texture_mesh_id, 0);

        for (int i = -thickness; i <= +thickness; i++)
        {
            for (int j = -thickness; j <= +thickness; j++)
            {
                if (i == 0 && j == 0)
                {
                    continue;
                }

                vec2 offset = vec2(i, j) * size;

                vec2 final_uv = v_uv + offset;
                if (final_uv[0] < 0) final_uv[0] = 0;
                if (final_uv[1] < 0) final_uv[1] = 0;
                //if (final_uv[0] < 0) final_uv[0] = 0;
                //if (final_uv[0] < 0) final_uv[0] = 0;


                // and if one of the neighboring pixels is white (we are on the border)
                if (texture(texture_mesh_id, final_uv).r == selected_mesh_id)
                {
                    frag_color = vec4(vec3(1.0f), 1.0f);
                    return;
                }
            }
        }
    }
}

#endif

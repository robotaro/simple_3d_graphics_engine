#version 400

#if defined VERTEX_SHADER

in vec3 in_position;
in vec3 in_normal;
in vec2 in_texcoord_0;

uniform mat4 projection_matrix;
uniform mat4 view_matrix;
uniform mat4 model_matrix;

out vec3 position;
out vec3 normal;
out vec2 uv;

void main() {
    vec4 point = view_matrix * model_matrix * vec4(in_position, 1.0);
    gl_Position = projection_matrix * point;
    // // We don't need to rotate normal matrix in this situation
    // mat3 normal_matrix = transpose(inverse(mat3(modelview)));
    // normal = normal_matrix * in_normal;
    normal = in_normal;
    uv = in_texcoord_0;
    position = point.xyz;
}

#elif defined FRAGMENT_SHADER

// These locations are the indices of the textures that are listed when the framebuffer is created
layout(location=0) out vec4 out_color;
layout(location=1) out vec4 out_normal;
layout(location=2) out vec4 out_position;

in vec3 position;
in vec3 normal;
in vec2 uv;

uniform sampler2D texture0;

void main() {
    out_color = texture(texture0, uv);
    out_normal = vec4(normalize(normal), 0.0);
    out_position = vec4(position, 0.0);
}
#endif

struct CameraSettings {
    mat4 projection_matrix;
    mat4 view_matrix;
    vec3 camera_position;
    float padding_0;
};

layout (std140, binding = 0) uniform CameraBlock {
    CameraSettings camera[4];
}camera_settings;

import moderngl
import numpy as np
from pyrr import Matrix44
from moderngl_window import WindowConfig, run_window_config

class InfiniteGrid(WindowConfig):
    gl_version = (3, 3)
    title = "Infinite Grid"
    window_size = (800, 600)
    aspect_ratio = 16 / 9

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prog = self.ctx.program(
            vertex_shader='''
            #version 330 core
            uniform mat4 view;
            uniform mat4 proj;

            out vec3 nearPoint;
            out vec3 farPoint;

            vec3 gridPlane[6] = vec3[](
                vec3(1, 1, 0), vec3(-1, -1, 0), vec3(-1, 1, 0),
                vec3(-1, -1, 0), vec3(1, 1, 0), vec3(1, -1, 0)
            );

            vec3 UnprojectPoint(float x, float y, float z, mat4 view, mat4 projection) {
                mat4 viewInv = inverse(view);
                mat4 projInv = inverse(projection);
                vec4 unprojectedPoint = viewInv * projInv * vec4(x, y, z, 1.0);
                return unprojectedPoint.xyz / unprojectedPoint.w;
            }

            void main() {
                vec3 p = gridPlane[gl_VertexID];
                nearPoint = UnprojectPoint(p.x, p.y, 0.0, view, proj);
                farPoint = UnprojectPoint(p.x, p.y, 1.0, view, proj);
                gl_Position = vec4(p, 1.0);
            }
            ''',
            fragment_shader='''
            #version 330 core

            in vec3 nearPoint;
            in vec3 farPoint;
            uniform mat4 view;
            uniform mat4 proj;
            uniform float near; // 0.01
            uniform float far;  // 100

            out vec4 outColor;

            vec4 grid(vec3 fragPos3D, float scale, bool drawAxis) {
                vec2 coord = fragPos3D.xz * scale;
                vec2 derivative = fwidth(coord);
                vec2 grid = abs(fract(coord - 0.5) - 0.5) / derivative;
                float line = min(grid.x, grid.y);
                float minimumz = min(derivative.y, 1.0);
                float minimumx = min(derivative.x, 1.0);
                vec4 color = vec4(0.2, 0.2, 0.2, 1.0 - min(line, 1.0));
                if (fragPos3D.x > -0.1 * minimumx && fragPos3D.x < 0.1 * minimumx)
                    color.z = 1.0;
                if (fragPos3D.z > -0.1 * minimumz && fragPos3D.z < 0.1 * minimumz)
                    color.x = 1.0;
                return color;
            }

            float computeDepth(vec3 pos) {
                vec4 clip_space_pos = proj * view * vec4(pos.xyz, 1.0);
                return (clip_space_pos.z / clip_space_pos.w);
            }

            float computeLinearDepth(vec3 pos) {
                vec4 clip_space_pos = proj * view * vec4(pos.xyz, 1.0);
                float clip_space_depth = (clip_space_pos.z / clip_space_pos.w) * 2.0 - 1.0; // put back between -1 and 1
                float linearDepth = (2.0 * near * far) / (far + near - clip_space_depth * (far - near)); // get linear value between 0.01 and 100
                return linearDepth / far; // normalize
            }

            void main() {
                float t = -nearPoint.y / (farPoint.y - nearPoint.y);
                vec3 fragPos3D = nearPoint + t * (farPoint - nearPoint);

                gl_FragDepth = computeDepth(fragPos3D);

                float linearDepth = computeLinearDepth(fragPos3D);
                float fading = max(0.0, (0.5 - linearDepth));

                outColor = (grid(fragPos3D, 10.0, true) + grid(fragPos3D, 1.0, true)) * float(t > 0.0); // adding multiple resolutions for the grid
                outColor.a *= fading;
            }
            '''
        )

        # Create an empty VBO and VAO (no actual vertex data is needed)
        self.vbo = self.ctx.buffer(reserve=6 * 3 * 4)  # 6 vertices, 3 components each, 4 bytes per component
        self.vao = self.ctx.vertex_array(self.prog, [(self.vbo, '3f', 'gridPlane')])

        self.prog['near'].value = 0.01
        self.prog['far'].value = 100.0

    def render(self, time, frametime):
        angle = time
        camera_distance = 10.0
        eye = (np.sin(angle) * camera_distance, 2.0, np.cos(angle) * camera_distance)
        target = (0.0, 0.0, 0.0)
        up = (0.0, 1.0, 0.0)

        view = Matrix44.look_at(eye, target, up)
        proj = Matrix44.perspective_projection(45.0, self.aspect_ratio, 0.01, 100.0)

        self.prog['view'].write(view.astype('f4').tobytes())
        self.prog['proj'].write(proj.astype('f4').tobytes())

        self.ctx.clear(0.0, 0.0, 0.0)
        self.vao.render(moderngl.TRIANGLES)

if __name__ == '__main__':
    run_window_config(InfiniteGrid)

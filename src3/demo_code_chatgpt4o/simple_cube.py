import numpy as np
import glm
import moderngl
import glfw
from glm import vec3, mat4

# Vertex data for an orange cube
vertices = np.array([
    # positions         # normals           # colors
    # Front face
    -1.0, -1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.5, 0.0,
    1.0, -1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.5, 0.0,
    1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.5, 0.0,
    -1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.5, 0.0,

    # Back face
    -1.0, -1.0, -1.0, 0.0, 0.0, -1.0, 1.0, 0.5, 0.0,
    1.0, -1.0, -1.0, 0.0, 0.0, -1.0, 1.0, 0.5, 0.0,
    1.0, 1.0, -1.0, 0.0, 0.0, -1.0, 1.0, 0.5, 0.0,
    -1.0, 1.0, -1.0, 0.0, 0.0, -1.0, 1.0, 0.5, 0.0,

    # Left face
    -1.0, -1.0, -1.0, -1.0, 0.0, 0.0, 1.0, 0.5, 0.0,
    -1.0, -1.0, 1.0, -1.0, 0.0, 0.0, 1.0, 0.5, 0.0,
    -1.0, 1.0, 1.0, -1.0, 0.0, 0.0, 1.0, 0.5, 0.0,
    -1.0, 1.0, -1.0, -1.0, 0.0, 0.0, 1.0, 0.5, 0.0,

    # Right face
    1.0, -1.0, -1.0, 1.0, 0.0, 0.0, 1.0, 0.5, 0.0,
    1.0, -1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.5, 0.0,
    1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.5, 0.0,
    1.0, 1.0, -1.0, 1.0, 0.0, 0.0, 1.0, 0.5, 0.0,

    # Top face
    -1.0, 1.0, -1.0, 0.0, 1.0, 0.0, 1.0, 0.5, 0.0,
    -1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.5, 0.0,
    1.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.5, 0.0,
    1.0, 1.0, -1.0, 0.0, 1.0, 0.0, 1.0, 0.5, 0.0,

    # Bottom face
    -1.0, -1.0, -1.0, 0.0, -1.0, 0.0, 1.0, 0.5, 0.0,
    -1.0, -1.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.5, 0.0,
    1.0, -1.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.5, 0.0,
    1.0, -1.0, -1.0, 0.0, -1.0, 0.0, 1.0, 0.5, 0.0,
], dtype='f4')

indices = np.array([
    # Front face
    0, 1, 2, 2, 3, 0,
    # Back face
    4, 5, 6, 6, 7, 4,
    # Left face
    8, 9, 10, 10, 11, 8,
    # Right face
    12, 13, 14, 14, 15, 12,
    # Top face
    16, 17, 18, 18, 19, 16,
    # Bottom face
    20, 21, 22, 22, 23, 20
], dtype='i4')

# Vertex and fragment shader source code
vertex_shader_code = """
#version 430
layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec3 in_color;

out vec3 normal;
out vec3 color;
out vec3 fragPos;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

void main() {
    fragPos = vec3(m_model * vec4(in_position, 1.0));
    normal = mat3(transpose(inverse(m_model))) * normalize(in_normal);
    color = in_color;
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}
"""

fragment_shader_code = """
#version 430
layout (location = 0) out vec4 fragColor;

in vec3 normal;
in vec3 color;
in vec3 fragPos;

struct Light {
    vec3 position;
    vec3 Ia;
    vec3 Id;
    vec3 Is;
};

uniform Light light;
uniform vec3 camPos;

vec3 getLight(vec3 color) {
    vec3 Normal = normalize(normal);

    // ambient light
    vec3 ambient = light.Ia;

    // diffuse light
    vec3 lightDir = normalize(light.position - fragPos);
    float diff = max(0, dot(lightDir, Normal));
    vec3 diffuse = diff * light.Id;

    // specular light
    vec3 viewDir = normalize(camPos - fragPos);
    vec3 reflectDir = reflect(-lightDir, Normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0), 32);
    vec3 specular = spec * light.Is;

    return color * (ambient + (diffuse + specular));
}

void main() {
    float gamma = 2.2;
    vec3 final_color = pow(color, vec3(gamma));

    final_color = getLight(final_color);

    final_color = pow(final_color, 1 / vec3(gamma));
    fragColor = vec4(final_color, 1.0);
}
"""

def main():
    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "Orange Cube", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    ctx = moderngl.create_context()

    prog = ctx.program(
        vertex_shader=vertex_shader_code,
        fragment_shader=fragment_shader_code
    )

    vbo = ctx.buffer(vertices.tobytes())
    ibo = ctx.buffer(indices.tobytes())

    vao = ctx.vertex_array(prog, [
        (vbo, '3f 3f 3f', 'in_position', 'in_normal', 'in_color')
    ], ibo)

    light = {
        'position': vec3(1.0, 1.0, 1.0),
        'Ia': vec3(0.2, 0.2, 0.2),
        'Id': vec3(0.5, 0.5, 0.5),
        'Is': vec3(1.0, 1.0, 1.0),
    }

    prog['light.position'].value = vec3(1.0, 1.0, 1.0)
    prog['light.Ia'].value = vec3(0.2, 0.2, 0.2)
    prog['light.Id'].value = vec3(0.5, 0.5, 0.5)
    prog['light.Is'].value = vec3(1.0, 1.0, 1.0)
    prog['camPos'].value = (0.0, 0.0, 3.0)

    projection = glm.perspective(glm.radians(45.0), 800/600, 0.1, 100.0)
    view = glm.inverse(glm.translate(glm.mat4(1.0), glm.vec3(2.0, 0.0, 10.0)))
    model = glm.mat4(1.0)

    prog['m_proj'].write(projection)
    prog['m_view'].write(view)
    prog['m_model'].write(model)

    while not glfw.window_should_close(window):
        ctx.clear(0.1, 0.1, 0.1)
        vao.render(moderngl.TRIANGLES)
        glfw.swap_buffers(window)
        glfw.poll_events()
        print(glfw.window_should_close(window))

    print("Window terminated")
    glfw.terminate()

if __name__ == "__main__":
    main()
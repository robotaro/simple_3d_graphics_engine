# Shader sources
vertex_shader_source = """
#version 330

uniform mat4 uViewProjMatrix;

layout(location = 0) in vec4 aPositionSize;
layout(location = 1) in vec4 aColor;

out VertexData {
    noperspective float m_edgeDistance;
    noperspective float m_size;
    smooth vec4 m_color;
} vData;

void main() {
    vData.m_color = aColor.abgr; // swizzle to correct endianness
    vData.m_color.a *= smoothstep(0.0, 1.0, aPositionSize.w / 2.0);
    vData.m_size = max(aPositionSize.w, 2.0);
    gl_Position = uViewProjMatrix * vec4(aPositionSize.xyz, 1.0);
}
"""

geometry_shader_source = """
#version 330

layout(lines) in;
layout(triangle_strip, max_vertices = 4) out;

uniform vec2 uViewport;

in VertexData {
    noperspective float m_edgeDistance;
    noperspective float m_size;
    smooth vec4 m_color;
} vData[];

out VertexData {
    noperspective float m_edgeDistance;
    noperspective float m_size;
    smooth vec4 m_color;
} vDataOut;

void main() {
    vec2 pos0 = gl_in[0].gl_Position.xy / gl_in[0].gl_Position.w;
    vec2 pos1 = gl_in[1].gl_Position.xy / gl_in[1].gl_Position.w;

    vec2 dir = pos1 - pos0;
    dir = normalize(vec2(dir.x, dir.y * uViewport.y / uViewport.x)); // correct for aspect ratio
    vec2 tng0 = vec2(-dir.y, dir.x) * vData[0].m_size / uViewport;
    vec2 tng1 = vec2(-dir.y, dir.x) * vData[1].m_size / uViewport;

    // Line start
    gl_Position = vec4((pos0 - tng0) * gl_in[0].gl_Position.w, gl_in[0].gl_Position.zw);
    vDataOut.m_edgeDistance = -vData[0].m_size;
    vDataOut.m_size = vData[0].m_size;
    vDataOut.m_color = vData[0].m_color;
    EmitVertex();

    gl_Position = vec4((pos0 + tng0) * gl_in[0].gl_Position.w, gl_in[0].gl_Position.zw);
    vDataOut.m_edgeDistance = vData[0].m_size;
    vDataOut.m_size = vData[0].m_size;
    vDataOut.m_color = vData[0].m_color;
    EmitVertex();

    // Line end
    gl_Position = vec4((pos1 - tng1) * gl_in[1].gl_Position.w, gl_in[1].gl_Position.zw);
    vDataOut.m_edgeDistance = -vData[1].m_size;
    vDataOut.m_size = vData[1].m_size;
    vDataOut.m_color = vData[1].m_color;
    EmitVertex();

    gl_Position = vec4((pos1 + tng1) * gl_in[1].gl_Position.w, gl_in[1].gl_Position.zw);
    vDataOut.m_edgeDistance = vData[1].m_size;
    vDataOut.m_size = vData[1].m_size;
    vDataOut.m_color = vData[1].m_color;
    EmitVertex();

    EndPrimitive();
}
"""

fragment_shader_source = """
#version 330

in VertexData {
    noperspective float m_edgeDistance;
    noperspective float m_size;
    smooth vec4 m_color;
} vData;

layout(location=0) out vec4 fResult;

void main() {
    fResult = vData.m_color;
    float d = abs(vData.m_edgeDistance) / vData.m_size;
    d = smoothstep(1.0, 1.0 - (2.0 / vData.m_size), d);
    fResult.a *= d;
}
"""

import moderngl
import numpy as np
import glm
import pygame
from pygame.locals import DOUBLEBUF, OPENGL

# Initialize Pygame and create an OpenGL context
pygame.init()
pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
ctx = moderngl.create_context()

# Compile shaders and create a program
prog = ctx.program(
    vertex_shader=vertex_shader_source,
    geometry_shader=geometry_shader_source,
    fragment_shader=fragment_shader_source,
)

# Define the circle's properties
radius = 0.5
segments = 100
angle_step = 2 * np.pi / segments
line_width = 3.0

# Generate circle points
circle_vertices = []
for i in range(segments):
    angle = i * angle_step
    x = radius * np.cos(angle)
    y = radius * np.sin(angle)
    circle_vertices.extend([x, y, 0.0, line_width])  # Last value is the line width
    circle_vertices.extend([1.0, 0.0, 0.0, 1.0])  # Red color with full alpha

    # Add the next point to close the line segment
    next_angle = (i + 1) * angle_step
    next_x = radius * np.cos(next_angle)
    next_y = radius * np.sin(next_angle)
    circle_vertices.extend([next_x, next_y, 0.0, line_width])
    circle_vertices.extend([1.0, 0.0, 0.0, 1.0])

# Convert to numpy array
circle_vertices = np.array(circle_vertices, dtype='f4')

# Create a buffer and a vertex array
vbo = ctx.buffer(circle_vertices.tobytes())
vao = ctx.simple_vertex_array(prog, vbo, 'aPositionSize', 'aColor')

# Setup the camera (view and projection matrices)
camera_pos = glm.vec3(3, 3, 3)
look_at = glm.vec3(0, 0, 0)
up = glm.vec3(0, 1, 0)

view = glm.lookAt(camera_pos, look_at, up)
proj = glm.perspective(glm.radians(45.0), 800 / 600, 0.1, 100.0)
view_proj = proj * view

# Pass the view_proj matrix to the shader
prog['uViewProjMatrix'].write(view_proj.to_bytes())

# Pass the viewport size to the geometry shader
prog['uViewport'].value = (800, 600)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    ctx.clear(0.0, 0.0, 0.0, 1.0)

    # Draw the circle
    vao.render(moderngl.LINES)

    # Swap buffers
    pygame.display.flip()

pygame.quit()

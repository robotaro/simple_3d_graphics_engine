from glm import vec3, vec4, mat4, length, length2, inverse, translate, scale, dot, normalize, sin, cos, cross
import numpy as np

from src3 import math_3d
from src3.gizmos import gizmo_constants

def generate_disk_vertex_data(radius: float,
                              num_segments: int,
                              origin: vec3,
                              direction: vec3,
                              line_width: float,
                              color: tuple) -> np.ndarray:
    # Ensure the direction vector is normalized
    direction = normalize(direction)

    # Find a vector orthogonal to the direction vector to start the circle generation
    if abs(direction.x) > abs(direction.z):
        ortho = vec3(-direction.y, direction.x, 0)
    else:
        ortho = vec3(0, -direction.z, direction.y)

    ortho = normalize(ortho)
    bitangent = cross(direction, ortho)

    # Generate the circle points
    vertices = []
    for i in range(num_segments):
        angle1 = 2.0 * np.pi * i / num_segments
        angle2 = 2.0 * np.pi * (i + 1) / num_segments

        x1 = radius * cos(angle1)
        y1 = radius * sin(angle1)
        point1 = origin + x1 * ortho + y1 * bitangent

        x2 = radius * cos(angle2)
        y2 = radius * sin(angle2)
        point2 = origin + x2 * ortho + y2 * bitangent

        vertex1 = [point1.x, point1.y, point1.z, line_width] + list(color)
        vertex2 = [point2.x, point2.y, point2.z, line_width] + list(color)

        vertices.append(vertex1)
        vertices.append(vertex2)

    return np.array(vertices, dtype=np.float32)
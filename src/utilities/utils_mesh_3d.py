import os
import numpy as np
import trimesh
import pywavefront

from src.core import constants


def create_box(width=1.0, height=1.0, depth=1.0):

    result = trimesh.creation.box()
    vertices = np.array(result.vertices).astype('f4')
    indices = np.array(result.faces).astype('i4')

    vertices *= np.array((width, height, depth), dtype=np.float32)

    new_vertices, new_normals, _ = convert_faces_to_triangles(vertices=vertices, uvs=None, faces=indices)

    return new_vertices, new_normals, None, None


def create_icosphere(radius: float, subdivisions: int) -> tuple:

    result = trimesh.creation.icosphere(radius=radius, subdivisions=subdivisions)

    vertices = np.array(result.vertices).astype('f4')
    normals = np.array(result.vertex_normals).astype('f4')
    uvs = None
    indices = np.array(result.faces).astype('i4')

    return vertices, normals, uvs, indices


def create_cylinder(point_a: tuple, point_b:tuple, radius: float, sections: int) -> tuple:

    result = trimesh.creation.cylinder(segment=(point_a, point_b), radius=radius, sections=sections)

    vertices = np.array(result.vertices).astype('f4')
    indices = np.array(result.faces).astype('i4')

    new_vertices, new_normals, new_uvs = convert_faces_to_triangles(vertices=vertices, uvs=None, faces=indices)

    return new_vertices, new_normals, None, None


def create_capsule(height: float, radius: float, count: tuple) -> tuple:

    # Incomplete !!!

    result = trimesh.creation.capsule(height, radius, count, None)

    vertices = np.array(result.vertices).astype('f4')
    normals = np.array(result.vertex_normals).astype('f4')
    uvs = None
    indices = np.array(result.faces).astype('i4')

    return vertices, normals, uvs, indices

def convert_faces_to_triangles(vertices, uvs, faces):
    """
    From ChatGPT: This function takes the input vertices and UVs that share common vertex normals and
    recreate a list of triangles with unique normals for each vertex. UVs are also modified+ to follow
    the same logic
    """

    # Calculate flat normals for each face
    face_normals = np.cross(vertices[faces[:, 1]] - vertices[faces[:, 0]],
                            vertices[faces[:, 2]] - vertices[faces[:, 0]])
    face_normals /= np.linalg.norm(face_normals, axis=1)[:, np.newaxis]

    # Initialize arrays for the new vertices, normals, and UVs
    new_vertices = []
    new_normals = []
    new_uvs = []

    # Iterate through each face and populate the new arrays
    for i in range(len(faces)):
        face = faces[i]
        face_normal = face_normals[i]

        for vertex_idx in face:
            new_vertices.append(vertices[vertex_idx])
            new_normals.append(face_normal)
            if uvs is not None and len(uvs) > 0:
                new_uvs.append(uvs[vertex_idx])

    # Convert the lists to NumPy arrays
    new_vertices = np.array(new_vertices, dtype=np.float32)
    new_normals = np.array(new_normals, dtype=np.float32)
    new_uvs = np.array(new_uvs, dtype=np.float32)

    return new_vertices, new_normals, new_uvs
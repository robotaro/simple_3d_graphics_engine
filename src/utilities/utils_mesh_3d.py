import os
import numpy as np
import trimesh
import pywavefront

from src.core import constants


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
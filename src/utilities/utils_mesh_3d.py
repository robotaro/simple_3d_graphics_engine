import os
import numpy as np
import trimesh

from src import constants


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


def from_obj(fpath: str, scale=1.0) -> tuple:

    # First try the fpath as a relative path from RESOURCES, and if it not there, assume fpath is an absolute path
    os_compatible_fpath = fpath.replace("\\", os.sep).replace("/", os.sep)
    new_fpath = os.path.join(constants.RESOURCES_DIR, os_compatible_fpath)
    if os.path.isfile(new_fpath):
        mesh = trimesh.load(new_fpath)
    else:
        mesh = trimesh.load(fpath)

    vertices = np.array(mesh.vertices, dtype=np.float32)
    normals = np.array(mesh.vertex_normals, dtype=np.float32)
    uvs = None
    if "uv" in mesh.visual.__dict__:
        uvs = np.array(mesh.visual.uv, dtype=np.float32)
    indices = np.array(mesh.faces, dtype=np.int32)

    return vertices, normals, uvs, indices


def from_gltf(fpath: str, scale=1.0) -> tuple:

    """
    Loads a GLTF/GLB file and combines all meshes into one.

    :param fpath:
    :param scale:
    :return:
    """

    # First try the fpath as a relative path from RESOURCES, and if it not there, assume fpath is an absolute path
    os_compatible_fpath = fpath.replace("\\", os.sep).replace("/", os.sep)
    new_fpath = os.path.join(constants.RESOURCES_DIR, os_compatible_fpath)
    if os.path.isfile(new_fpath):
        scene = trimesh.load(new_fpath)
    else:
        scene = trimesh.load(fpath)

    meshes = list(scene.geometry.values())

    # Combine all meshes into one. For now.
    vertices = np.concatenate([mesh.vertices for mesh in meshes], axis=0, dtype=np.float32) * scale
    normals = np.concatenate([mesh.vertex_normals for mesh in meshes], axis=0, dtype=np.float32)

    faces_list = []
    sum_num_faces = 0
    for mesh in meshes:
        faces_list.append(mesh.faces + sum_num_faces)
        sum_num_faces += mesh.vertices.shape[0]
    indices = np.concatenate(faces_list, axis=0)

    uvs = None
    uv_list = []
    for mesh in meshes:
        if "uv" in mesh.visual.__dict__:
            uv_list.append(mesh.visual.uv)
    if len(uv_list) > 0:
        uvs = np.concatenate([uv for uv in uv_list], axis=0, dtype=np.float32)

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
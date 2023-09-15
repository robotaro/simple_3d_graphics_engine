import os
import numpy as np
import trimesh

from ecs import constants


class MeshFactory:

    """
    A simple class designed to load meshes
    """

    def __init__(self):
        pass

    @staticmethod
    def create_cube(width: float, height: float, depth: float) -> tuple:

        result = trimesh.creation.box(extents=(width, height, depth))

        vertices = np.array(result.vertices).astype('f4')
        normals = np.array(result.vertex_normals).astype('f4')
        uvs = None
        indices = np.array(result.faces).astype('i4')

        return vertices, normals, uvs, indices

    @staticmethod
    def create_icosphere(radius: float, subdivisions: int) -> tuple:

        result = trimesh.creation.icosphere(radius=radius, subdivisions=subdivisions)

        vertices = np.array(result.vertices).astype('f4')
        normals = np.array(result.vertex_normals).astype('f4')
        uvs = None
        indices = np.array(result.faces).astype('i4')

        return vertices, normals, uvs, indices

    @staticmethod
    def from_obj(fpath: str) -> tuple:

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

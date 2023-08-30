import numpy as np
import trimesh


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
    def from_obj(fpath: str) -> tuple:
        mesh = trimesh.load(fpath)

        vertices = np.array(mesh.vertices, dtype=np.float32)
        normals = np.array(mesh.vertex_normals, dtype=np.float32)
        uvs = None
        if "uv" in mesh.visual.__dict__:
            uvs = np.array(mesh.visual.uv, dtype=np.float32)
        indices = np.array(mesh.faces, dtype=np.int32)

        return vertices, normals, uvs, indices

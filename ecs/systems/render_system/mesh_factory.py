import numpy as np
import trimesh


class MeshFactory:

    """
    A simple class designed to load meshes
    """

    def __init__(self):
        pass

    def create_cube(self, width: float, height: float, depth: float) -> tuple:
        raise NotImplemented("[ERROR] MeshFactory.create_cube() not implemented yet")

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

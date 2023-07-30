import os
import numpy as np
import trimesh

from core.mesh import Mesh


class MeshLoader:

    def __init__(self):
        pass

    def from_obj(self, fpath: str, scale=1.0) -> Mesh:
        mesh = trimesh.load(fpath, process=False)

        vertices = np.array(mesh.vertices, dtype=np.float32)
        normals = np.array(mesh.vertex_normals, dtype=np.float32)
        faces = np.array(mesh.faces, dtype=np.int32)
        uvs = None

        if "uv" in mesh.visual.__dict__:
            uvs = np.array(mesh.visual.uv, dtype=np.float32)
        return vertices, normals, faces, uvs

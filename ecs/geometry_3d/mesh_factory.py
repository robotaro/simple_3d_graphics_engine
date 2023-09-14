import os
import numpy as np
import trimesh

from ecs.components.mesh import Mesh


class MeshFactory:

    def __init__(self):
        pass

    def create_cube(self, width: float, height: float, depth: float) -> Mesh:
        raise NotImplemented("[ERROR] MeshFactory.create_cube() not implemented yet")

    def from_obj(self, fpath: str, name="", program_name="mesh") -> Mesh:
        mesh = trimesh.load(fpath)

        vertices = np.array(mesh.vertices, dtype=np.float32)
        normals = np.array(mesh.vertex_normals, dtype=np.float32)
        faces = np.array(mesh.faces, dtype=np.int32)
        uvs = None

        if "uv" in mesh.visual.__dict__:
            uvs = np.array(mesh.visual.uv, dtype=np.float32)

        new_mesh = Mesh(
            name=name,
            forward_pass_program_name=program_name,
            vertices=vertices,
            normals=normals,
            faces=faces,
            uvs=uvs)

        if len(new_mesh.name) == 0:
            new_mesh.name = f"mesh{new_mesh.uid}"

        return new_mesh

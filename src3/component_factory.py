import moderngl
import numpy as np

from src3.components.mesh_component import MeshComponent
from src3.components.transform import Transform
from src3.components.material import Material
from src3.shader_loader import ShaderLoader



class ComponentFactory:

    def __init__(self,
                 ctx: moderngl.Context,
                 shader_loader: ShaderLoader):
        self.ctx = ctx
        self.shader_loader = shader_loader

    def create_transform(self, position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
        return Transform(position, rotation, scale)

    def create_material(self, color=(1, 1, 1), texture=None):
        return Material(color, texture)

    def create_mesh(self, vertices: np.array, normals=None, colors=None, indices=None) -> MeshComponent:
        mesh = MeshComponent(
            ctx=self.ctx,
            vertices=vertices,
            normals=normals,
            colors=colors,
            indices=indices
        )

        for shader_program_name, shader_program in self.shader_loader.shaders.items():
            mesh.create_vao(
                shader_program_name=shader_program_name,
                shader_program=shader_program
            )

        return mesh
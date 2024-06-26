import moderngl
import numpy as np

from src3.components.mesh_component import MeshComponent
from src3.components.transform_component import TransformComponent
from src3.components.material_component import MaterialComponent
from src3.shader_loader import ShaderLoader


class ComponentFactory:

    def __init__(self,
                 ctx: moderngl.Context,
                 shader_loader: ShaderLoader):
        self.ctx = ctx
        self.shader_loader = shader_loader

    def create_transform(self, position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
        transform = TransformComponent(position=position, rotation=rotation, scale=scale)
        transform.update()
        return transform

    def create_material(self, color=(1, 1, 1), texture=None):
        return MaterialComponent(color, texture)

    def create_mesh(self, vertices: np.array, normals=None, colors=None, indices=None) -> MeshComponent:
        mesh = MeshComponent(
            ctx=self.ctx,
            vertices=vertices,
            normals=normals,
            colors=colors,
            indices=indices)

        for shader_program_name, shader in self.shader_loader.shaders.items():
            mesh.create_vao(
                shader_program_name=shader_program_name,
                shader_program=shader.program)

        return mesh

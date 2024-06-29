import moderngl
import numpy as np
from glm import vec3, quat

from src3 import constants
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

    def create_transform(self, position=vec3(0, 0, 0), rotation=vec3(0, 0, 0), scale=vec3(1, 1, 1)):
        transform = TransformComponent(position=position,
                                       rotation=quat(rotation),
                                       scale=scale)
        return transform

    def create_material(self, color=(1, 1, 1), texture=None):
        return MaterialComponent(color, texture)

    def create_mesh(self,
                    vertices: np.array,
                    normals=None,
                    colors=None,
                    indices=None,
                    render_mode=constants.MESH_RENDER_MODE_TRIANGLES) -> MeshComponent:
        mesh = MeshComponent(
            ctx=self.ctx,
            vertices=vertices,
            normals=normals,
            colors=colors,
            indices=indices,
            render_mode=render_mode
        )

        for shader_program_name, shader in self.shader_loader.shaders.items():
            mesh.create_vao(
                shader_program_name=shader_program_name,
                shader_program=shader.program)

        return mesh

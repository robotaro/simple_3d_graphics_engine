import moderngl
import numpy as np
from glm import vec3, quat

from src3 import constants
from src3.components.mesh import Mesh
from src3.components.point_cloud_component import PointCloudComponent
from src3.components.transform import Transform
from src3.components.material_component import MaterialComponent
from src3.components.bezier_segment_component import BezierSegmentComponent
from src3.shader_loader import ShaderLoader


class ComponentFactory:

    def __init__(self,
                 ctx: moderngl.Context,
                 shader_loader: ShaderLoader):
        self.ctx = ctx
        self.shader_loader = shader_loader

    def create_transform(self, position=vec3(0, 0, 0), rotation=vec3(0, 0, 0), scale=vec3(1, 1, 1)):
        transform = Transform(position=position,
                              rotation=quat(rotation),
                              scale=scale)
        return transform

    def create_material(self, color=(1, 1, 1), texture=None):
        return MaterialComponent(color=color, texture=texture)

    def create_mesh(self,
                    vertices: np.array,
                    normals=None,
                    colors=None,
                    indices=None) -> Mesh:

        mesh = Mesh(
            ctx=self.ctx,
            program=self.shader_loader.get_program(shader_filename="basic.glsl"),
            vertices=vertices,
            normals=normals,
            colors=colors,
            indices=indices)

        for shader_program_name, shader in self.shader_loader.shaders.items():
            mesh.create_vao(shader_program=shader.program)

        return mesh

    def create_bezier_segment(self, control_points=None, num_segments=32):
        return BezierSegmentComponent(
            control_points=control_points,
            num_segments=num_segments)

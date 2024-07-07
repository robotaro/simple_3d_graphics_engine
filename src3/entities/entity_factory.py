import moderngl
import numpy as np
from glm import vec3

from src3 import constants
from src3.components.mesh_component import MeshComponent
from src3.components.point_cloud_component import PointCloudComponent
from src3.components.transform_component import TransformComponent
from src3.components.material_component import MaterialComponent
from src3.components.bezier_segment_component import BezierSegmentComponent

from src3 import constants
from src3.entities.entity import Entity
from src3.shader_loader import ShaderLoader
from src3.components.component_factory import ComponentFactory
from src3.mesh_factory_3d import MeshFactory3D


class EntityFactory:

    def __init__(self, ctx: moderngl.Context, shader_loader: ShaderLoader):
        self.ctx = ctx
        self.shader_loader = shader_loader
        self.component_factory = ComponentFactory(ctx=self.ctx, shader_loader=self.shader_loader)

    def create_renderable_from_gltf(self, fpath: str):
        pass

    def create_renderable_3d_axis(self, axis_radius=0.05, label="3d_axis"):
        mesh_factory = MeshFactory3D()
        shape_list = [
            {"name": "cylinder",
             "point_a": (0.0, 0.0, 0.0),
             "point_b": (1.0, 0.0, 0.0),
             "radius": axis_radius,
             "color": (1.0, 0.2, 0.2)},
            {"name": "cylinder",
             "point_a": (0.0, 0.0, 0.0),
             "point_b": (0.0, 1.0, 0.0),
             "radius": axis_radius,
             "color": (0.2, 1.0, 0.2)},
            {"name": "cylinder",
             "point_a": (0.0, 0.0, 0.0),
             "point_b": (0.0, 0.0, 1.0),
             "radius": axis_radius,
             "color": (0.2, 0.2, 1.0)}
        ]
        mesh_data = mesh_factory.generate_mesh(shape_list=shape_list)

        mesh_component = self.component_factory.create_mesh(
            vertices=mesh_data["vertices"],
            normals=mesh_data["normals"],
            colors=mesh_data["colors"])

        transform_component = self.component_factory.create_transform()

        return Entity(label=label,
                      archetype="renderable",
                      component_list=[mesh_component, transform_component])

    def create_sphere(self, radius: float, position: vec3, color: tuple, subdivisions=3, label="sphere"):
        mesh_factory = MeshFactory3D()
        shape_list = [
            {"name": "icosphere",
             "radius": radius,
             "subdivisions": subdivisions,
             "color": color}
        ]
        mesh_data = mesh_factory.generate_mesh(shape_list=shape_list)

        mesh_component = self.component_factory.create_mesh(
            vertices=mesh_data["vertices"],
            normals=mesh_data["normals"],
            colors=mesh_data["colors"])

        transform_component = self.component_factory.create_transform(position=position)

        return Entity(label=label,
                      archetype="renderable",
                      component_list=[mesh_component, transform_component])

    def create_grid_xz(self, num_cells: int, cell_size: float, grid_color=(0.3, 0.3, 0.3), label="grid"):
        mesh_factory = MeshFactory3D()
        mesh_data = mesh_factory.create_grid_xz(
            num_cells=num_cells,
            cell_size=cell_size,
            grid_color=grid_color)

        mesh_component = self.component_factory.create_mesh(
            vertices=mesh_data["vertices"],
            normals=mesh_data["normals"],
            colors=mesh_data["colors"],
            render_mode=constants.MESH_RENDER_MODE_LINES)

        transform_component = self.component_factory.create_transform()
        return Entity(label=label,
                      archetype="renderable",
                      component_list=[mesh_component, transform_component])

    def create_point_cloud(self, points: np.ndarray, colors: np.ndarray, label="point_cloud"):

        point_cloud_component = PointCloudComponent(
            ctx=self.ctx,
            shader_loader=self.shader_loader,
            points=points,
            colors=colors)

        transform_component = self.component_factory.create_transform(position=vec3(0, 0, 0))
        return Entity(label=label,
                      archetype="point_cloud",
                      component_list=[point_cloud_component, transform_component])

    def create_bezier_curve(self, origin: vec3, label="bezier_curve"):
        bezier_segment_component = self.component_factory.create_bezier_segment()
        transform_component = self.component_factory.create_transform(position=origin)
        return Entity(label=label,
                      archetype="renderable",
                      component_list=[bezier_segment_component, transform_component])
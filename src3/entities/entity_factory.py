import moderngl
from glm import vec3

from src3 import constants
from src3.entities.entity import Entity
from src3.shader_loader import ShaderLoader
from src3.components.component_factory import ComponentFactory
from src.geometry_3d.mesh_factory_3d import MeshFactory3D


class EntityFactory:

    def __init__(self, ctx: moderngl.Context, shader_loader: ShaderLoader):
        self.ctx = ctx
        self.shader_loader = shader_loader
        self.component_factory = ComponentFactory(ctx=self.ctx, shader_loader=self.shader_loader)

    def create_custom_entity(self, archetype: str, component_list: list):
        entity = Entity(archetype=archetype, component_list=component_list)
        return entity

    def create_renderable_from_gltf(self, fpath: str):
        pass

    def create_renderable_3d_axis(self, axis_radius=0.05):
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
            colors=mesh_data["colors"]
        )
        transform_component = self.component_factory.create_transform()
        return Entity(archetype="renderable", component_list=[mesh_component, transform_component])

    def create_sphere(self, radius: float, subdivisions=3):
        mesh_factory = MeshFactory3D()
        shape_list = [
            {"name": "icosphere",
             "radius": radius,
             "subdivisions": subdivisions,
             "color": (1.0, 0.5, 0.0)}
        ]
        mesh_data = mesh_factory.generate_mesh(shape_list=shape_list)

        mesh_component = self.component_factory.create_mesh(
            vertices=mesh_data["vertices"],
            normals=mesh_data["normals"],
            colors=mesh_data["colors"]
        )
        transform_component = self.component_factory.create_transform()
        return Entity(archetype="renderable", component_list=[mesh_component, transform_component])

    def create_grid_xz(self, num_cells: int, cell_size: float):
        mesh_factory = MeshFactory3D()
        mesh_data = mesh_factory.create_grid_xz(num_cells, cell_size)

        mesh_component = self.component_factory.create_mesh(
            vertices=mesh_data["vertices"],
            normals=mesh_data["normals"],
            colors=mesh_data["colors"],
            render_mode=constants.MESH_RENDER_MODE_LINES
        )
        transform_component = self.component_factory.create_transform()
        return Entity(archetype="renderable", component_list=[mesh_component, transform_component])
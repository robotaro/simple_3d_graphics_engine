import imgui
import os
import numpy as np
import moderngl
import glm
from glm import mat4, vec3

from src.geometry_3d.mesh_factory_3d import MeshFactory3D
from src3 import constants
from src3.io.gltf_reader import GLTFReader
from src3.editors.editor import Editor
from src3.components.component_factory import ComponentFactory
from src3.entities.entity_factory import EntityFactory


class Viewer3D(Editor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.window_size = (900, 600)
        self.fbo_size = (640, 480)
        self.program = self.shader_loader.get_program(shader_filename="basic.glsl")
        self.component_factory = ComponentFactory(ctx=self.ctx, shader_loader=self.shader_loader)
        self.entity_factory = EntityFactory(ctx=self.ctx)

        self.fbo = self.ctx.framebuffer(
            color_attachments=self.ctx.texture(self.fbo_size, 3),
            depth_attachment=self.ctx.depth_texture(self.fbo_size),
        )

        # Camera variables - temporary
        aspect_ratio = self.fbo_size[0] / self.fbo_size[1]
        self.projection_matrix = glm.perspective(glm.radians(45.0), aspect_ratio, 0.1, 100.0)
        self.view_matrix = glm.inverse(glm.translate(glm.mat4(1.0), glm.vec3(0.0, 1.0, 5.0)))

        self.entities = {}

        # System-only entities
        self.renderable_entity_grid = None

    def setup(self) -> bool:

        self.entities[1] = self.create_axis_entity()

        #gltf_fpath = os.path.join(constants.RESOURCES_DIR, "meshes", "situp_to_iddle.gltf")
        #self.entities[2] = self.load_gltf_entity(fpath=gltf_fpath)

        return True

    def create_axis_entity(self):
        mesh_factory = MeshFactory3D()
        radius = 0.1
        shape_list = [
            {"name": "cylinder",
             "point_a": (0.0, 0.0, 0.0),
             "point_b": (1.0, 0.0, 0.0),
             "radius": radius,
             "color": (1.0, 0.3, 0.3)},
            {"name": "cylinder",
             "point_a": (0.0, 0.0, 0.0),
             "point_b": (0.0, 1.0, 0.0),
             "radius": radius,
             "color": (0.3, 1.0, 0.3)},
            {"name": "cylinder",
             "point_a": (0.0, 0.0, 0.0),
             "point_b": (0.0, 0.0, 1.0),
             "radius": radius,
             "color": (0.3, 0.3, 1.0)}
        ]
        mesh_data = mesh_factory.generate_mesh(shape_list=shape_list)

        mesh_component = self.component_factory.create_mesh(
            vertices=mesh_data["vertices"],
            normals=mesh_data["normals"],
            colors=mesh_data["colors"]
        )
        transform_component = self.component_factory.create_transform()

        # Create entity
        return self.entity_factory.create_renderable(component_list=[mesh_component, transform_component])

    def load_gltf_entity(self, fpath: str):
        reader = GLTFReader()
        reader.load(gltf_fpath=fpath)
        meshes = reader.get_meshes()

        mesh_component = self.component_factory.create_mesh(
            vertices=meshes[-1]["attributes"]["POSITION"],
            normals=meshes[-1]["attributes"]["NORMAL"],
            indices=meshes[-1]["indices"].astype(np.uint32))
        transform_component = self.component_factory.create_transform()

        # Create entity
        return self.entity_factory.create_renderable(component_list=[mesh_component, transform_component])

    def update(self, time: float, elapsed_time: float):
        self.render_scene()
        self.render_ui()

    def shutdown(self):
        for _, entity in self.entities.items():
            entity.release()

    def render_scene(self):

        # Setup mvp cameras
        self.program["m_proj"].write(self.projection_matrix)
        self.program['m_view'].write(self.view_matrix)
        self.program['m_model'].write(glm.mat4(1.0))

        # Setup lights
        self.program["light.position"].value = (10.0, 10.0, -10.0)
        self.program['light.position'].value = vec3(1.0, 1.0, 1.0)
        self.program['light.Ia'].value = vec3(0.2, 0.2, 0.2)
        self.program['light.Id'].value = vec3(0.5, 0.5, 0.5)
        self.program['light.Is'].value = vec3(1.0, 1.0, 1.0)
        self.program['camPos'].value = (0.0, 0.0, 3.0)

        self.fbo.use()
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.fbo.clear()

        # Render renderable entities
        for entity_id, entity in self.entities.items():
            entity.comp_mesh.render(shader_program_name="basic.glsl")

    def render_ui(self):

        imgui.begin("Viewer 3D", True)
        imgui.set_window_size(self.window_size[0], self.window_size[1])

        # Left Column - Menus
        with imgui.begin_group():
            imgui.push_style_var(imgui.STYLE_FRAME_BORDERSIZE, 1.0)
            imgui.text("Entities")
            with imgui.begin_list_box("", 200, 100) as list_box:
                if list_box.opened:
                    imgui.selectable("Selected", True)
                    imgui.selectable("Not Selected", False)
            imgui.pop_style_var(1)

        imgui.same_line(spacing=20)

        # Right Column - 3D Scene
        with imgui.begin_group():
            texture_id = self.fbo.color_attachments[0].glo

            # NOTE: I'm using the uv0 and uv1 arguments to FLIP the image back vertically, as it is flipped by default
            imgui.image(texture_id, *self.fbo.size, uv0=(0, 1), uv1=(1, 0))

        imgui.end()

    
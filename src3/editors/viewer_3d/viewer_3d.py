import imgui
import os
import numpy as np
import glm
from glm import mat4, vec3

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
        self.view_matrix = glm.inverse(glm.translate(glm.mat4(1.0), glm.vec3(2.0, 0.0, 10.0)))

        self.entities = {}

        # System-only entities
        self.renderable_entity_grid = None

    def setup(self) -> bool:

        # Generate components
        reader = GLTFReader()
        gltf_fpath = os.path.join(constants.RESOURCES_DIR, "meshes", "situp_to_iddle.gltf")
        reader.load(gltf_fpath=gltf_fpath)
        meshes = reader.get_meshes()

        mesh_component = self.component_factory.create_mesh(
            vertices=meshes[-1]["attributes"]["POSITION"],
            normals=meshes[-1]["attributes"]["NORMAL"],
            indices=meshes[-1]["indices"].astype(np.uint32))
        transform_component = self.component_factory.create_transform()

        # Create entity
        self.entities[1] = self.entity_factory.create_renderable(
            component_list=[mesh_component, transform_component])

        return True

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
            imgui.image(self.fbo.color_attachments[0].glo, *self.fbo.size)

        imgui.end()

    
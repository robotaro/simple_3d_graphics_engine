import moderngl

from src.core import constants
from src2.render_stages.render_stage import RenderStage


class RenderStageSelection(RenderStage):

    name = "selection_pass"

    __slots__ = [
        "texture_color",
        "texture_depth",
        "framebuffer"
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialise framebuffers
        self.update_framebuffer(window_size=kwargs["initial_window_size"])

    def update_framebuffer(self, window_size: tuple):

        # Release any existing textures and framebuffers first
        self.release()

        # Before re-creating them
        self.textures["color"] = self.ctx.texture(size=window_size, components=4, dtype='f4')
        self.textures["color"].filter = (moderngl.NEAREST, moderngl.NEAREST)  # No interpolation!
        self.textures["color"].repeat_x = False  # This prevents outlining from spilling over to the other edge
        self.textures["color"].repeat_y = False
        self.textures["depth"] = self.ctx.depth_texture(size=window_size)
        self.framebuffer = self.ctx.framebuffer(
            color_attachments=[
                self.textures["color"]
            ],
            depth_attachment=self.textures["depth"])

    def render(self):

        self.framebuffer.use()

        for render_layer in self.render_layers:

            # Setup viewport
            self.framebuffer.viewport = render_layer.viewport.viewport_pixels

            # Setup camera
            camera = render_layer.viewport.camera
            camera_transform = camera["transform"]
            self.program["projection_matrix"].write(camera.get_projection_matrix().T.tobytes())
            self.program["view_matrix"].write(camera_transform.inverse_world_matrix.T.tobytes())
            self.program["camera_position"].value = camera_transform.position

            self.framebuffer.clear(
                depth=1.0,
                viewport=render_layer.viewport.viewport_pixels)

            # Render entities
            for entity_group in render_layer.entity_groups:

                if not entity_group.visible:
                    continue

                for entity in entity_group.entities:

                    if not entity.visible:
                        continue

                    self.program["model_matrix"].write(entity["transform"].world_matrix.T.tobytes())

                    # TODO: Check render_mode: mesh_component.vaos[constants.SHADER_PROGRAM_SELECTED_ENTITY_PASS].render(mode=mesh_component.render_mode)
                    self.program["instanced"] = entity.num_instances > 1
                    entity.render(vao_name=constants.SHADER_PROGRAM_SELECTED_ENTITY_PASS,
                                  num_instances=entity.num_instances)

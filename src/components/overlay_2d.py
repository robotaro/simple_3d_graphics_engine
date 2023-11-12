import numpy as np

from src.core import constants
from src.components.component import Component
from src.systems.render_system.font_library import FontLibrary
from src.systems.render_system.im_overlay_2d import ImOverlay2D


class Overlay2D(Component):

    _type = "overlay_2d"

    __slots__ = [
        "im_overlay",
        "font_name",
        "render_layer",
        "visible",
        "vao",
        "vbo"
    ]

    def __init__(self, parameters, system_owned=False):

        super().__init__(parameters=parameters, system_owned=system_owned)

        self.im_overlay = ImOverlay2D()

        # TODO: User standard method for retrieving parameter values
        self.font_name = parameters.get("font_name", constants.FONT_DEFAULT_NAME)
        self.render_layer = 0
        self.visible = True
        self.vao = None
        self.vbo = None

    def initialise(self, **kwargs):

        if self.initialised:
            return

        ctx = kwargs["ctx"]
        shader_library = kwargs["shader_library"]
        font_library = kwargs["font_library"]

        self.im_overlay.register_font(font_library.fonts[self.font_name].character_data)

        self.vbo = ctx.buffer(reserve=constants.OVERLAY_2D_VBO_SIZE_RESERVE)  # TODO: Check this size
        program = shader_library[constants.SHADER_PROGRAM_OVERLAY_2D_PASS]

        self.vao = ctx.vertex_array(program,
                                    self.vbo,
                                    "in_command_id",
                                    "in_position",
                                    "in_size",
                                    "in_color",
                                    "in_edge_width",
                                    "in_uv_min",
                                    "in_uv_max")

        self.initialised = True

    def update_buffer(self):

        if self.im_overlay.num_draw_commands > 0:
            self.vbo.write(self.im_overlay.draw_commands[:self.im_overlay.num_draw_commands, :].tobytes())

    def clear(self):
        self.im_overlay.clear()

    def release(self):
        if self.vbo:
            self.vbo.release()

        if self.vao:
            self.vbo.release()


import moderngl
import numpy as np

from src.core import constants
from src.components.component import Component
from src.systems.render_system.shader_program_library import ShaderProgramLibrary
from src.systems.render_system.font_library import FontLibrary
from src.utilities.utils_im_overlay_2d import ImOverlay2D

class Overlay2D(Component):

    _type = "overlay_2d"

    __slots__ = [
        "im_overlay",
        "font_name",
        "position",
        "render_layer",
        "visible",
        "vao",
        "vbo",
        "text",
        "dirty"
    ]

    def __init__(self, parameters, system_owned=False):

        super().__init__(parameters=parameters, system_owned=system_owned)

        self.im_overlay = ImOverlay2D()

        # TODO: User standard method for retrieving parameter values
        self.font_name = parameters.get("font_name", constants.FONT_DEFAULT_NAME)
        self.position = Component.dict2tuple_float(input_dict=self.parameters,
                                                   key="position",
                                                   default_value=(0.0, 0.0))
        self.render_layer = 0
        self.visible = True
        self.vao = None
        self.vbo = None
        self.text = parameters.get("text", "")
        self.dirty = False if len(self.text) == 0 else True

    def initialise(self, **kwargs):

        if self.initialised:
            return

        ctx = kwargs["ctx"]
        shader_library = kwargs["shader_library"]

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

    def update_buffer(self, font_library: FontLibrary):

        if not self.initialised or not self.dirty:
            return

        # [DEBUG]
        self.im_overlay.clear()
        self.im_overlay.add_aabb_filled(600.0, 100.0, 200.0, 100.0, (1.0, 0.65, 0.0, 0.3))
        self.im_overlay.add_aabb_edge(600.0, 300.0, 200.0, 100.0, 2.0, (1.0, 0.0, 0.0, 1.0))
        self.im_overlay.add_aabb_filled(600.0, 600.0, 200.0, 100.0, (0.0, 1.0, 0.0, 0.6))

        text_data = font_library.generate_text_vbo_data(font_name=self.font_name,
                                                        text=self.text,
                                                        position=self.position)

        new_columns = np.ones((text_data.shape[0], ), dtype=np.float32)
        text_data = np.insert(text_data, 0, new_columns, axis=1)
        text_data = np.ascontiguousarray(text_data)

        #self.vbo.write(text_data[:, :9].tobytes())
        self.vbo.write(self.im_overlay.draw_commands[:self.im_overlay.num_draw_commands, :].tobytes())

    def set_text(self, text: str) -> None:
        self.text = text
        self.dirty = True

    def release(self):
        if self.vbo:
            self.vbo.release()

        if self.vao:
            self.vbo.release()


from typing import Dict, Optional, Any
import moderngl


class Component:

    __slots__ = [
        "ctx",
        "data_manager",
        "shader_library",
        "params"
    ]

    def __init__(self,
                 ctx:  Optional[moderngl.Context] = None,
                 data_manager: Optional[Any] = None,
                 shader_library: Optional[Any] = None,
                 params: Optional[Dict] = None):
        self.ctx = ctx
        self.data_manager = data_manager
        self.shader_library = shader_library
        self.params = params if params is not None else {}

    def initialise(self, **kwargs):
        pass

    def draw_imgui_properties(self, imgui):
        pass

    def release(self):
        pass

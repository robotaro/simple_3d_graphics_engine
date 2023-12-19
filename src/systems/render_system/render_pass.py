import moderngl
from abc import ABC, abstractmethod

from src.core.scene import Scene


class RenderPass(ABC):
    __slots__ = [
        "materials_ubo",
        "point_lights_ubo",
        "directional_lights_ubo",
        "transforms_ubo",
        "ctx",
        "shader_program_library"
    ]

    def __init__(self, **kwargs):
        self.ctx = kwargs["ctx"]
        self.shader_program_library = kwargs["shader_program_library"]

    @abstractmethod
    def create_framebuffers(self, window_size: tuple):
        pass

    @abstractmethod
    def render(self,
               scene: Scene,
               materials_ubo: moderngl.Buffer,
               point_lights_ubo: moderngl.Buffer,
               transforms_ubo: moderngl.Buffer):
        pass

    @abstractmethod
    def release(self):
        pass

    @staticmethod
    def safe_release(mgl_object):
        if mgl_object is not None:
            mgl_object.release()
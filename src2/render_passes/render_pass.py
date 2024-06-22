from typing import Optional, Dict, List
import moderngl
from abc import ABC, abstractmethod

from src2.core.scene import Scene
from src2.core.shader_program_library import ShaderProgramLibrary


class RenderPass(ABC):

    __slots__ = [
        "program",
        "ctx",
        "ubos",
        "framebuffer",
        "framebuffer_is_external",
        "textures",
        "texture_is_external",
        "shader_program_library",
        "render_layers",
        "ready_to_render"
    ]

    def __init__(self,
                 ctx: moderngl.Context,
                 shader_library: ShaderProgramLibrary,
                 initial_window_size: tuple,  # (width, height)
                 render_layers: Optional[List] = None,
                 input_framebuffer: Optional[moderngl.Framebuffer] = None,
                 input_textures: Optional[Dict] = None,
                 ubos: Optional[Dict] = None):

        self.program = None
        self.shader_program_library = shader_library
        self.ctx = ctx
        self.framebuffer = input_framebuffer
        self.framebuffer_is_external = False
        self.textures = {} if input_textures is None else input_textures
        self.texture_is_external = {}
        self.ubos = ubos
        self.render_layers = [] if render_layers is None else render_layers

        # Process any external framebuffer
        if self.framebuffer is not None:
            self.framebuffer_is_external = True

        # Process any external textures
        for texture_name, texture in self.textures.items():
            self.texture_is_external[texture_name] = True

        self.update_window_size(window_size=initial_window_size)

    @abstractmethod
    def update_window_size(self, window_size: tuple):
        pass

    @abstractmethod
    def render(self, scene: Scene):
        pass

    def release(self):
        for texture_name, texture in self.textures.items():
            # Only release textures that were created in this stage
            if self.texture_is_external.get(texture_name, False):
                continue
            texture.release()

        if self.framebuffer is not None and not self.framebuffer_is_external:
            self.framebuffer.release()

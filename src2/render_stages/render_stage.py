from typing import Optional, Dict
import moderngl
from abc import ABC, abstractmethod

from src2.core.shader_program_library import ShaderProgramLibrary


class RenderStage(ABC):

    __slots__ = [
        "program",
        "ctx",
        "framebuffer",
        "framebuffer_is_external",
        "textures",
        "texture_is_external",
        "shader_program_library",
        "render_layers"
    ]

    def __init__(self,
                 ctx: moderngl.Context,
                 shader_library: ShaderProgramLibrary,
                 render_layers: Optional[Dict] = None,
                 framebuffer: Optional[moderngl.Framebuffer] = None,
                 textures: Optional[Dict] = None):

        self.program = None
        self.shader_program_library = shader_library
        self.ctx = ctx
        self.textures = {}
        self.texture_is_external = {}
        self.framebuffer = None
        self.framebuffer_is_external = False
        self.render_layers = render_layers

        # Process any external framebuffer
        if framebuffer is not None:
            self.framebuffer = framebuffer
            self.framebuffer_is_external = True

        # Process any external textures
        if isinstance(textures, dict):
            for texture_name, texture in textures.items():
                self.textures[texture_name] = texture_name
                self.texture_is_external[texture_name] = True

    @abstractmethod
    def update_framebuffer(self, window_size: tuple):
        pass

    @abstractmethod
    def render(self):
        pass

    def release(self):
        for texture_name, texture in self.textures.items():
            # Only release textures that were created in this stage
            if self.texture_is_external[texture_name]:
                continue
            texture.release()

        if self.framebuffer is not None and not self.framebuffer_is_external:
            self.framebuffer.release()

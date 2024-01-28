from typing import Dict, Optional
from abc import ABC, abstractmethod
import moderngl

from src2.core.shader_program_library import ShaderProgramLibrary
from src2.entities.entity import Entity
from src2.render_stages.render_stage import RenderStage
from src2.render_stages.render_stage_forward import RenderStageForward
from src2.render_stages.render_stage_selection import RenderStageSelection
from src2.render_stages.render_stage_overlay import RenderStageOverlay
from src2.render_stages.render_stage_shadow import RenderStageShadow
from logging import Logger


class Scene(ABC):

    __slots__ = [
        "name",
        "params",
        "ctx",
        "shader_library",
        "logger",
        "registered_render_stages",
        "render_stages",
        "render_stage_order"
    ]

    def __init__(self,
                 logger: Logger,
                 shader_library: ShaderProgramLibrary,
                 ctx: moderngl.Context,
                 name: Optional[str] = None,
                 params: Optional[Dict] = None):

        self.name = name
        self.params = params if params else {}
        self.ctx = ctx
        self.shader_library = shader_library
        self.logger = logger
        self.registered_render_stages = {}
        self.render_stages = []

        self.register_render_stage_type(name="forward", render_stage_class=RenderStageForward)
        self.register_render_stage_type(name="selection", render_stage_class=RenderStageSelection)
        self.register_render_stage_type(name="overlay", render_stage_class=RenderStageOverlay)
        self.register_render_stage_type(name="shadow", render_stage_class=RenderStageShadow)

    def render(self):

        for render_stage in self.render_stages:
            render_stage.render()

    def update_window_size(self, window_size: tuple):
        pass

    def register_render_stage_type(self, name: str, render_stage_class):
        if name in self.registered_render_stages:
            raise KeyError(f"[ERROR] RenderStage type {name} already registered")
        self.registered_render_stages[name] = render_stage_class

    def create_render_stage(self, name: str, stage_type: str, framebuffer=None, textures=None) -> RenderStage:
        if name in self.render_stages:
            raise KeyError(f"[ERROR] RenderStage {name} already exists")

        new_render_stage = self.registered_render_stages[stage_type](
            ctx=self.ctx,
            shader_library=self.shader_library,
            textures=textures,
            framebuffer=framebuffer,
        )

        self.render_stages[name] = new_render_stage
        return new_render_stage

    def attach_entity(self, name: str, entity: Entity):
        pass

    def detach_entity(self, name: str):
        pass

    def validate_render_stages(self) -> bool:
        """
        Checks if all texture and framebuffer connections between render stages, if any , are valid
        :return:
        """
        return False

    def destroy(self):
        pass

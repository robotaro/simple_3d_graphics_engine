from typing import Dict, Optional
from abc import ABC
import moderngl
from logging import Logger

from src2.core.shader_program_library import ShaderProgramLibrary
from src2.entities.entity import Entity
from src2.render_stages.render_stage_forward import RenderStageForward
from src2.render_stages.render_stage_selection import RenderStageSelection
from src2.render_stages.render_stage_overlay import RenderStageOverlay
from src2.render_stages.render_stage_shadow import RenderStageShadow
from src2.render_stages.render_stage_screen import RenderStageScreen


class Scene(ABC):

    __slots__ = [
        "params",
        "ctx",
        "ubos",
        "shader_library",
        "logger",
        "registered_render_stage_types",
        "render_stages",
        "render_stage_order",
        "initial_window_size"
    ]

    def __init__(self,
                 logger: Logger,
                 shader_library: ShaderProgramLibrary,
                 ctx: moderngl.Context,
                 initial_window_size: tuple,
                 ubos: dict,
                 params: Optional[Dict] = None):

        self.params = params if params else {}
        self.ctx = ctx
        self.shader_library = shader_library
        self.logger = logger
        self.registered_render_stage_types = {}
        self.ubos = ubos
        self.render_stages = {}
        self.initial_window_size = initial_window_size

        self.register_render_stage_type(name="forward", render_stage_class=RenderStageForward)
        self.register_render_stage_type(name="selection", render_stage_class=RenderStageSelection)
        self.register_render_stage_type(name="overlay", render_stage_class=RenderStageOverlay)
        self.register_render_stage_type(name="shadow", render_stage_class=RenderStageShadow)
        self.register_render_stage_type(name="screen", render_stage_class=RenderStageScreen)

    def render(self):
        for render_stage in self.render_stages:
            render_stage.render()

    def update_window_size(self, window_size: tuple):
        for render_stage in self.render_stages:
            render_stage.update_framebuffer(window_size=window_size)

    def register_render_stage_type(self, name: str, render_stage_class):
        if name in self.registered_render_stage_types:
            raise KeyError(f"[ERROR] RenderStage type {name} already registered")
        self.registered_render_stage_types[name] = render_stage_class

    def attach_entity(self, entity_id: str, entity: Entity):
        pass

    def detach_entity(self, entity_id: str):
        pass

    def destroy(self):
        pass

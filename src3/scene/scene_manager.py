"""
Manager for multiple scenes and scene operations
"""
import logging
from typing import Dict, Optional
import moderngl

from src3.scene.scene import Scene
from src3.shader_loader import ShaderLoader
from src3.ubo_manager import UBOManager


class SceneManager:
    """
    Manages multiple scenes and scene switching
    """

    def __init__(self,
                 ctx: moderngl.Context,
                 shader_loader: ShaderLoader,
                 ubo_manager: UBOManager,
                 logger: Optional[logging.Logger] = None):

        self.ctx = ctx
        self.shader_loader = shader_loader
        self.ubo_manager = ubo_manager
        self.logger = logger or logging.getLogger(__name__)

        self._scenes: Dict[str, Scene] = {}
        self._active_scene_name: Optional[str] = None

    def create_scene(self, name: str) -> Scene:
        """Create a new scene"""
        if name in self._scenes:
            self.logger.warning(f"Scene '{name}' already exists")
            return self._scenes[name]

        scene = Scene(
            ctx=self.ctx,
            shader_loader=self.shader_loader,
            ubo_manager=self.ubo_manager,
            logger=self.logger
        )
        scene.settings.name = name

        self._scenes[name] = scene

        # Set as active if it's the first scene
        if self._active_scene_name is None:
            self._active_scene_name = name

        self.logger.info(f"Created scene '{name}'")
        return scene

    def get_scene(self, name: str) -> Optional[Scene]:
        """Get scene by name"""
        return self._scenes.get(name)

    def get_active_scene(self) -> Optional[Scene]:
        """Get the currently active scene"""
        if self._active_scene_name:
            return self._scenes.get(self._active_scene_name)
        return None

    def set_active_scene(self, name: str) -> bool:
        """Set the active scene"""
        if name not in self._scenes:
            self.logger.error(f"Scene '{name}' does not exist")
            return False

        self._active_scene_name = name
        self.logger.info(f"Active scene set to '{name}'")
        return True

    def delete_scene(self, name: str) -> bool:
        """Delete a scene"""
        if name not in self._scenes:
            return False

        scene = self._scenes[name]
        scene.clear()
        del self._scenes[name]

        # Update active scene if needed
        if self._active_scene_name == name:
            self._active_scene_name = next(iter(self._scenes.keys())) if self._scenes else None

        self.logger.info(f"Deleted scene '{name}'")
        return True

    def list_scenes(self) -> list:
        """Get list of all scene names"""
        return list(self._scenes.keys())
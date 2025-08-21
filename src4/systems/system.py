# ecs/system.py
"""Base system class"""
from abc import ABC, abstractmethod

from src4.world import World
from src4.components.transform import Transform
from src4.components.renderable import Renderable
from src4.components.hierarchy import Hierarchy


class System(ABC):
    """
    Base system class. Systems contain logic that operates on components.
    Systems are coarse-grained, handling broad domains of functionality.
    """

    def __init__(self, world: World):
        self.world = world

    @abstractmethod
    def update(self, delta_time: float):
        """Update the system"""
        pass

    def process_dirty_entities(self, dirty_flag: str, process_func):
        """Helper to process dirty entities"""
        dirty_set = self.world.get_dirty_set(dirty_flag)
        for entity_id in dirty_set:
            process_func(entity_id)
        self.world.clear_dirty(dirty_flag)

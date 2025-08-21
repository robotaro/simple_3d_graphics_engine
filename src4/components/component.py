# ecs/component.py
"""Base component class with serialization"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json


class Component(ABC):
    """
    Base component class. Components are pure data containers.
    Each component knows how to serialize/deserialize itself.
    """

    @abstractmethod
    def serialize(self) -> Dict[str, Any]:
        """Serialize component to a dictionary"""
        pass

    @abstractmethod
    def deserialize(self, data: Dict[str, Any]):
        """Deserialize component from a dictionary"""
        pass

    def get_dirty_flags(self) -> List[str]:
        """Return list of dirty flags this component affects when changed"""
        return []

    def clone(self) -> 'Component':
        """Create a deep copy of this component"""
        data = self.serialize()
        new_component = self.__class__()
        new_component.deserialize(data)
        return new_component
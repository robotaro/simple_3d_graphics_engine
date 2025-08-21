from typing import List, Optional, Dict, Any
from src4.world import World
from src4.components.component import Component


class Hierarchy(Component):
    """Complete hierarchy relationship component"""

    def __init__(self):
        self.parent_id: Optional[int] = None
        self.children_ids: List[int] = []
        # Note: siblings can be derived from parent's children list

    def add_child(self, child_id: int):
        """Add a child to this entity"""
        if child_id not in self.children_ids:
            self.children_ids.append(child_id)

    def remove_child(self, child_id: int):
        """Remove a child from this entity"""
        if child_id in self.children_ids:
            self.children_ids.remove(child_id)

    def get_siblings(self, world: 'World') -> List[int]:
        """Get sibling entities (requires world reference to check parent)"""
        if self.parent_id is None:
            return []

        parent_hierarchy = world.get_component(self.parent_id, Hierarchy)
        if parent_hierarchy:
            return [child_id for child_id in parent_hierarchy.children_ids
                    if child_id != self.entity_id]
        return []

    def serialize(self) -> Dict[str, Any]:
        return {
            "parent_id": self.parent_id,
            "children_ids": self.children_ids.copy()
        }

    def deserialize(self, data: Dict[str, Any]):
        self.parent_id = data.get("parent_id")
        self.children_ids = data.get("children_ids", []).copy()

    def get_dirty_flags(self) -> List[str]:
        return ["hierarchy", "transform"]
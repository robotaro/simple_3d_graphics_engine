"""
Scene node for hierarchy management
"""
from typing import Optional, List, Any


class SceneNode:
    """
    Node in the scene hierarchy tree
    Manages parent-child relationships between entities
    """

    def __init__(self, entity_id: int, entity: Any):
        self.entity_id = entity_id
        self.entity = entity
        self.parent: Optional[SceneNode] = None
        self.children: List[SceneNode] = []
        self.enabled = True
        self.visible = True

    def add_child(self, child: 'SceneNode'):
        """Add a child node"""
        if child not in self.children:
            self.children.append(child)
            child.parent = self

    def remove_child(self, child: 'SceneNode'):
        """Remove a child node"""
        if child in self.children:
            self.children.remove(child)
            child.parent = None

    def get_depth(self) -> int:
        """Get depth in hierarchy"""
        depth = 0
        current = self.parent
        while current:
            depth += 1
            current = current.parent
        return depth

    def get_path(self) -> str:
        """Get path from root to this node"""
        path_parts = []
        current = self
        while current:
            path_parts.append(current.entity.label)
            current = current.parent
        return '/'.join(reversed(path_parts))

    def traverse(self, callback, depth: int = 0):
        """
        Traverse hierarchy depth-first

        Args:
            callback: Function to call for each node (node, depth)
            depth: Current depth
        """
        callback(self, depth)
        for child in self.children:
            child.traverse(callback, depth + 1)

    def find_child_by_label(self, label: str) -> Optional['SceneNode']:
        """Find child node by entity label"""
        for child in self.children:
            if child.entity.label == label:
                return child
            # Recursive search
            found = child.find_child_by_label(label)
            if found:
                return found
        return None
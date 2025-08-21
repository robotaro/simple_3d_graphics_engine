from typing import List, Dict, Any
from src4.components.component import Component


class Transform(Component):
    """3D transform component"""

    def __init__(self):
        self.position = [0.0, 0.0, 0.0]
        self.rotation = [0.0, 0.0, 0.0]
        self.scale = [1.0, 1.0, 1.0]
        # Cached world matrix (computed by TransformSystem)
        self.world_matrix = None

    def serialize(self) -> Dict[str, Any]:
        return {
            "position": self.position.copy(),
            "rotation": self.rotation.copy(),
            "scale": self.scale.copy()
        }

    def deserialize(self, data: Dict[str, Any]):
        self.position = data["position"].copy()
        self.rotation = data["rotation"].copy()
        self.scale = data["scale"].copy()

    def get_dirty_flags(self) -> List[str]:
        return ["transform", "render"]
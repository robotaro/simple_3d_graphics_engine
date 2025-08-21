from typing import List, Optional, Dict, Any
from src4.components.component import Component


class InScene(Component):
    """Scene tagging component"""

    def __init__(self, scene_name: str = "default"):
        self.scene_name = scene_name

    def serialize(self) -> Dict[str, Any]:
        return {"scene_name": self.scene_name}

    def deserialize(self, data: Dict[str, Any]):
        self.scene_name = data["scene_name"]
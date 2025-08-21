from typing import List, Dict, Any
from src4.components.component import Component


class Visible(Component):
    """Visibility component"""

    def __init__(self, visible: bool = True):
        self.visible = visible

    def serialize(self) -> Dict[str, Any]:
        return {"visible": self.visible}

    def deserialize(self, data: Dict[str, Any]):
        self.visible = data["visible"]

    def get_dirty_flags(self) -> List[str]:
        return ["visibility", "render"]
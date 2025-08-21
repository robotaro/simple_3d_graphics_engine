from typing import List, Dict, Any
from component import Component


class Mesh(Component):
    """Mesh component storing VAO reference"""

    def __init__(self, mesh_name: str = ""):
        self.mesh_name = mesh_name
        self.vao = None  # Set by MeshSystem when loading

    def serialize(self) -> Dict[str, Any]:
        return {"mesh_name": self.mesh_name}

    def deserialize(self, data: Dict[str, Any]):
        self.mesh_name = data["mesh_name"]

    def get_dirty_flags(self) -> List[str]:
        return ["render"]
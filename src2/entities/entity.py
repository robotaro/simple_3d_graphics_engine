from typing import Dict, Optional


class Entity:

    __slots__ = [
        "params",
        "components",
        "num_instances",
        "ready_to_render",
        "dirty"
    ]

    def __init__(self, params: Optional[Dict] = None):
        self.params = {} if params is None else params
        self.components = {}
        self.num_instances = 1  # TODO: Declare this value in parameters?

        self.ready_to_render = False
        self.dirty = True

    def render(self):
        if not self.ready_to_render:
            return

        mesh = self.components.get("mesh", None)
        if not mesh:
            return

        mesh.render()


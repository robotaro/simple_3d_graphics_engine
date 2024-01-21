from typing import Dict, Optional


class Entity:

    __slots__ = [
        "name",
        "params",
        "components",
        "ready_to_render_flag",
        "dirty_flag"
    ]

    def __init__(self, name: Optional[str] = None, params: Optional[Dict] = None):
        self.name = "no_name" if name is None else params
        self.params = {} if params is None else params
        self.components = {}
        self.ready_to_render_flag = False
        self.dirty_flag = True

    def render(self):
        if not self.ready_to_render_flag:
            return


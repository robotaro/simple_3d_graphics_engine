from typing import Dict, Optional


class Entity:

    def __init__(self, name: Optional[str] = None, params: Optional[Dict] = None):
        self.name = "no_name" if name is None else params
        self.params = {} if params is None else params
        self.components = {}
        self.dirty_flag = True
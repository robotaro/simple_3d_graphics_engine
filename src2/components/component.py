from typing import Dict, Optional, Any
from src.core import constants
from src.utilities import utils_string


class Component:

    __slots__ = [
        "name",
        "params",
        "initialised",
        "system_owned"
    ]

    def __init__(self, name: Optional[str] = None, params: Optional[Dict] = None):
        self.name = name
        self.params = params if params is not None else {}
        self.initialised = False

    def initialise(self, **kwargs):
        pass

    def draw_imgui_properties(self, imgui):
        pass

    def release(self):
        pass

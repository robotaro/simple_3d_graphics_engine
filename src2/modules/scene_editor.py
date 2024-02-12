import logging
import moderngl
from collections import deque

from src2.modules.module import Module


class SceneEditor(Module):

    module_label = "Scene Editor"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)



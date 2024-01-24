import moderngl as mgl
from src2.core.viewport import Viewport


class RenderLayer:

    def __init__(self, viewport: Viewport):
        self.viewport = viewport
        self.point_lights = {}
        self.directional_lights = {}
        self.entity_groups = []

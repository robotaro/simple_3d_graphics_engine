import moderngl
import numpy as np
import trimesh

from core.camera import Camera, PerspectiveCamera, OrthographicCamera
from core.light import DirectionalLight
from core.node import Node
from core.utilities import utils_colors


class Scene:

    __slots__ = [
        "name",
        "uid_counter",
        "_meshes",
        "_directional_lights",
        "_cameras",
        "_root_node",
        "_background_color",
        "_ambient_light_color"
    ]

    def __init__(self,
                 name: str,
                 background_color=(1.0, 1.0, 1.0),
                 ambient_light_color=(1.0, 1.0, 1.0)):

        self.name = name
        self.uid_counter = 0

        # Internal Nodes
        self._meshes = []
        self._directional_lights = []
        self._cameras = []

        # Nodes
        self._root_node = Node(name="root_node")

        # Lighting
        self._background_color = background_color
        self._ambient_light_color = ambient_light_color

        # Flags

    # =========================================================================
    #                         Setters and getters
    # =========================================================================

    def get_nodes_by_type(self, node_type: str) -> list:
        meshes = []
        self._root_node.get_nodes_by_type(node_type=node_type, output_list=meshes)
        return meshes

    # =========================================================================
    #                         Create functions
    # =========================================================================

    def create_directional_light(self,
                                 name: str,
                                 direction=(-1.0, -1.0, -1.0),
                                 color=(1.0, 1.0, 1.0),
                                 intensity=0.5) -> DirectionalLight:

        new_light = DirectionalLight(name=name,
                                     color=color,
                                     intensity=intensity,
                                     direction=direction)

        self._directional_lights.append(new_light)

        return new_light

    def create_perspective_camera(self,
                                  name: str,
                                  position=(5, 5, 5),
                                  aspect_ratio=800/600,
                                  target=(0, 0, 0),
                                  y_pov_deg=45.0) -> PerspectiveCamera:

        new_camera = PerspectiveCamera(name=name,
                                       y_fov_deg=y_pov_deg,
                                       position=position,
                                       aspect_ratio=aspect_ratio)

        self._cameras.append(new_camera)

        return new_camera


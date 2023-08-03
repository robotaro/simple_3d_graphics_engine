import moderngl
import numpy as np
import trimesh

from core.mesh import Mesh
from core.camera import PerspectiveCamera, OrthographicCamera
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
                                  look_at=(0, 0, 0),
                                  y_pov_deg=45.0) -> PerspectiveCamera:

        new_camera = PerspectiveCamera(name=name, y_fov_deg=y_pov_deg)

        self._cameras.append(new_camera)

        return new_camera

    # =========================================================================
    #                           Rendering Functions
    # =========================================================================

    def render(self, context: moderngl.Context, camera: Camera):

        # REMEMBER THIS:  Scene rendering is during the FORWARD PASS!

        light_nodes = []
        self._root_node.get_nodes_by_type(type="directional_light", output_list=light_nodes)

        renderable_nodes = []
        self._root_node.get_nodes_by_type(type="mesh", output_list=renderable_nodes)

        # Set lights

        # Stage: Draw opaque objects first
        g = 0


        # Stage: Draw transparent objects back to front

        # TODO: Group renderables per program and render them all in batches to minimise program switching
        prog["ambient_strength"] = ambient_strength

        # =====================
        self._root_node.render_forward_pass()  # A simple placeholder recursive rendering

    def clear(self):
        """Clear out all nodes to form an empty scene.
        """
        self._root_node = Node()

        self._name_to_nodes = {}
        self._obj_to_nodes = {}
        self._obj_name_to_nodes = {}
        self._meshes = set()
        self._point_light_nodes = set()
        self._spot_light_nodes = set()
        self._directional_lights = set()
        self._cameras = set()
        self._main_camera_node = None

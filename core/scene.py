import moderngl
import numpy as np
import trimesh

from core.mesh import Mesh
from core.camera import Camera
from core.light import Light
from core.node import Node
from core.utilities import utils_colors


class Scene(object):

    def __init__(self,
                 name=None,
                 bg_color=None,
                 ambient_light=None):

        if bg_color is None:
            bg_color = np.ones(4)
        else:
            bg_color = utils_colors.format_color_vector(bg_color, 4)

        if ambient_light is None:
            ambient_light = np.zeros(3)

        self.root_node = Node(name="root_node")
        self.bg_color = bg_color
        self.ambient_light = ambient_light
        self.name = name

        self._name_to_nodes = {}
        self._obj_to_nodes = {}
        self._obj_name_to_nodes = {}
        self._mesh_nodes = set()
        self._point_light_nodes = set()
        self._spot_light_nodes = set()
        self._directional_light_nodes = set()
        self._camera_nodes = set()
        self._main_camera_node = None
        self._bounds = None

        # Transform tree
        self._path_cache = {}

    @property
    def name(self):
        """str : The user-defined name of this object.
        """
        return self._name

    @name.setter
    def name(self, value):
        if value is not None:
            value = str(value)
        self._name = value

    @property
    def nodes(self):
        """set of :class:`Node` : Set of nodes in the scene.
        """
        return self._nodes

    @property
    def bg_color(self):
        """(3,) float : The scene background color.
        """
        return self._bg_color

    @bg_color.setter
    def bg_color(self, value):
        if value is None:
            value = np.ones(4)
        else:
            value = utils_colors.format_color_vector(value, 4)
        self._bg_color = value

    @property
    def ambient_light(self):
        """(3,) float : The ambient light in the scene.
        """
        return self._ambient_light

    @ambient_light.setter
    def ambient_light(self, value):
        if value is None:
            value = np.zeros(3)
        else:
            value = utils_colors.format_color_vector(value, 3)
        self._ambient_light = value

    @property
    def meshes(self):
        """set of :class:`Mesh` : The meshes in the scene.
        """
        return set([n.mesh for n in self.mesh_nodes])

    @property
    def mesh_nodes(self):
        """set of :class:`Node` : The nodes containing meshes.
        """
        return self._mesh_nodes

    @property
    def lights(self):
        """set of :class:`Light` : The lights in the scene.
        """
        return self.point_lights | self.spot_lights | self.directional_lights

    @property
    def light_nodes(self):
        """set of :class:`Node` : The nodes containing lights.
        """
        return (self.point_light_nodes | self.spot_light_nodes |
                self.directional_light_nodes)

    @property
    def point_lights(self):
        """set of :class:`PointLight` : The point lights in the scene.
        """
        return set([n.light for n in self.point_light_nodes])

    @property
    def point_light_nodes(self):
        """set of :class:`Node` : The nodes containing point lights.
        """
        return self._point_light_nodes

    @property
    def spot_lights(self):
        """set of :class:`SpotLight` : The spot lights in the scene.
        """
        return set([n.light for n in self.spot_light_nodes])

    @property
    def spot_light_nodes(self):
        """set of :class:`Node` : The nodes containing spot lights.
        """
        return self._spot_light_nodes

    @property
    def directional_lights(self):
        """set of :class:`DirectionalLight` : The directional lights in
        the scene.
        """
        return set([n.light for n in self.directional_light_nodes])

    @property
    def directional_light_nodes(self):
        """set of :class:`Node` : The nodes containing directional lights.
        """
        return self._directional_light_nodes

    @property
    def cameras(self):
        """set of :class:`Camera` : The cameras in the scene.
        """
        return set([n.camera for n in self.camera_nodes])

    @property
    def camera_nodes(self):
        """set of :class:`Node` : The nodes containing cameras in the scene.
        """
        return self._camera_nodes

    @property
    def main_camera_node(self):
        """set of :class:`Node` : The node containing the main camera in the
        scene.
        """
        return self._main_camera_node

    @main_camera_node.setter
    def main_camera_node(self, value):
        if value not in self.nodes:
            raise ValueError('New main camera node must already be in scene')
        self._main_camera_node = value

    @property
    def bounds(self):
        """(2,3) float : The axis-aligned bounds of the scene.
        """
        if self._bounds is None:
            # Compute corners
            corners = []
            for mesh_node in self.mesh_nodes:
                mesh = mesh_node.mesh
                pose = self.get_pose(mesh_node)
                corners_local = trimesh.bounds.corners(mesh.bounds)
                corners_world = pose[:3, :3].dot(corners_local.T).T + pose[:3,3]
                corners.append(corners_world)
            if len(corners) == 0:
                self._bounds = np.zeros((2,3))
            else:
                corners = np.vstack(corners)
                self._bounds = np.array([np.min(corners, axis=0),
                                         np.max(corners, axis=0)])
        return self._bounds

    @property
    def centroid(self):
        """(3,) float : The centroid of the scene's axis-aligned bounding box
        (AABB).
        """
        return np.mean(self.bounds, axis=0)

    @property
    def extents(self):
        """(3,) float : The lengths of the axes of the scene's AABB.
        """
        return np.diff(self.bounds, axis=0).reshape(-1)

    @property
    def scale(self):
        """(3,) float : The length of the diagonal of the scene's AABB.
        """
        return np.linalg.norm(self.extents)

    def render(self, context: moderngl.Context, camera: Camera):

        # Stage: Get renderable Nodes
        renderable_nodes = []
        self.root_node.get_nodes_by_type(type="mesh", output_list=renderable_nodes)

        # Stage: Draw opaque objects first
        g = 0


        # Stage: Draw transparent objects back to front

        # =====================
        self.root_node.render()  # A simple placeholder recursive rendering

    def clear(self):
        """Clear out all nodes to form an empty scene.
        """
        self.root_node = Node()

        self._name_to_nodes = {}
        self._obj_to_nodes = {}
        self._obj_name_to_nodes = {}
        self._mesh_nodes = set()
        self._point_light_nodes = set()
        self._spot_light_nodes = set()
        self._directional_light_nodes = set()
        self._camera_nodes = set()
        self._main_camera_node = None
        self._bounds = None

        # Transform tree
        self._path_cache = {}

import numpy as np
import moderngl

from core.settings import SETTINGS
from ecs.math import node_math
from core.shader_library import ShaderLibrary


class Node:

    # TODO: Add slots here

    _type = "node"

    def __init__(self,
                 name=None,
                 rotation=None,
                 scale=None,
                 position=None,
                 matrix=None):

        self.uid = SETTINGS.next_gui_id()

        self._name = name
        self._parent = None
        self._children = []

        self._transform = None
        self._scale = None
        self._rotation = None
        self._position = None

        if matrix is None:
            if rotation is None:
                rotation = np.array([0.0, 0.0, 0.0, 1.0])
            if position is None:
                position = np.zeros(3)
            if scale is None:
                scale = np.ones(3)
            self.rotation = rotation
            self.translation = position
            self.scale = scale
        else:
            self.matrix = matrix

        # Rendering variables
        self._vbo_vertices = None
        self._vbo_normals = None
        self._vbo_colors = None
        self._vbo_indices = None
        self._vao = None
        self._prog = None
        self._num_instances = 1

        # Common flags
        self._visible = True
        self._ready_to_render = False
        self._selectable = True
        self._selected = False

    def add(self, child_node: "Node"):
        child_node.parent = self
        self._children.append(child_node)

    # =========================================================================
    #                         Utility functions
    # =========================================================================

    def get_nodes_by_type(self, node_type: str, output_list: list) -> None:

        if self._type == node_type:
            output_list.append(self)

        for child in self._children:
            child.get_nodes_by_type(node_type=node_type, output_list=output_list)

    def get_node_by_name(self, name: str) -> "Node":

        if self._name == name:
            return self

        for child in self._children:
            child.get_node_by_name(name=name)

    @staticmethod
    def once(func):
        def _decorator(self, *args, **kwargs):
            if self._ready_to_render:
                return
            else:
                func(self, *args, **kwargs)
                self._ready_to_render = True

        return _decorator

    # =========================================================================
    #                          Rendering Functions
    # =========================================================================

    def make_renderable(self, mlg_context: moderngl.Context, shader_library: ShaderLibrary, **kwargs):
        # TODO: The order should be controlled by the
        for child in self._children:
            child.make_renderable(mlg_context=mlg_context, shader_library=shader_library, **kwargs)

    def upload_buffers(self):
        pass

    def upload_uniform(self):
        pass

    def callback_immediate_mode_ui(self):
        pass

    # =========================================================================
    #                          Getters and Setters
    # =========================================================================

    @property
    def name(self):
        """str : The user-defined name of this object.
        """
        return self._name

    @name.setter
    def name(self, value):
        """str : The user-defined name of this object.
        """
        self._name = value

    @property
    def parent(self):
        """str : The user-defined name of this object.
        """
        return self._parent

    @parent.setter
    def parent(self, value):
        """str : The user-defined name of this object.
        """
        if not isinstance(value, Node):
            raise Exception(f"[ERROR] Parent is not a node type")
        self._parent = value

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        value = np.asanyarray(value)
        if value.shape != (4,):
            raise ValueError('Quaternion must be a (4,) vector')
        if np.abs(np.linalg.norm(value) - 1.0) > 1e-3:
            raise ValueError('Quaternion must have norm == 1.0')
        self._rotation = value
        self._transform = None

    @property
    def position(self):
        """(3,) float : The translation for this node.
        """
        return self._position

    @position.setter
    def position(self, value):
        value = np.asanyarray(value)
        if value.shape != (3,):
            raise ValueError('Translation must be a (3,) vector')
        self._position = value
        self._transform = None

    @property
    def scale(self):
        """(3,) float : The scale for this node.
        """
        return self._scale

    @scale.setter
    def scale(self, value):
        value = np.asanyarray(value)
        if value.shape != (3,):
            raise ValueError('Scale must be a (3,) vector')
        self._scale = value
        self._transform = None

    @property
    def transform(self):
        """(4,4) float : The homogenous transform matrix for this node.

        Note that this matrix's elements are not settable,
        it's just a copy of the internal matrix. You can set the whole
        matrix, but not an individual element.
        """
        if self._transform is None:
            self._transform = node_math.tqs2matrix(
                translation=self.translation,
                quaternion=self.rotation,
                scale=self.scale)
        return self._transform.copy()

    @transform.setter
    def transform(self, value):
        value = np.asanyarray(value)
        if value.shape != (4, 4):
            raise ValueError('Matrix must be a 4x4 numpy ndarray')
        if not np.allclose(value[3, :], np.array([0.0, 0.0, 0.0, 1.0])):
            raise ValueError('Bottom row of matrix must be [0,0,0,1]')
        self.rotation = node_math.matrix2quaternion(value)
        self.scale = node_math.matrix2scale(value)
        self.translation = node_math.matrix2translation(value)
        self._transform = value

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value: bool):
        self._visible = value

    # =========================================================================
    #                               Debug Functions
    # =========================================================================

    def print_hierarchy(self, level=0):
        """
        Prints all node hierarchy from this node downwards
        :return:
        """
        spacing = "".join(["  " for _ in range(level)])
        print(f"{spacing}> [{self._type}] Name: '{self.name}' | ID: {self.uid}")

        for child in self._children:
            child.print_hierarchy(level=(level + 1))




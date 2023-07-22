from core.settings import SETTINGS
import numpy as np
from core.math import node_math


class Node:

    def __init__(self,
                 name=None,
                 rotation=None,
                 scale=None,
                 translation=None,
                 matrix=None):

        self.name = name
        self.uid = SETTINGS.next_gui_id()
        self.children = []

        self._transform = None
        self._scale = None
        self._rotation = None
        self._translation = None

        if matrix is None:
            if rotation is None:
                rotation = np.array([0.0, 0.0, 0.0, 1.0])
            if translation is None:
                translation = np.zeros(3)
            if scale is None:
                scale = np.ones(3)
            self.rotation = rotation
            self.translation = translation
            self.scale = scale
        else:
            self.matrix = matrix

        # Common flags
        self._visible = True
        self._selectable = True
        self._selected = False
        self._dirty_flag = True
        self._instanced = False

    def add(self, child_node: "Node"):
        self.children.append(child_node)

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
    def camera(self):
        """:class:`Camera` : The camera in this node.
        """
        return self._camera

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
    def translation(self):
        """(3,) float : The translation for this node.
        """
        return self._translation

    @translation.setter
    def translation(self, value):
        value = np.asanyarray(value)
        if value.shape != (3,):
            raise ValueError('Translation must be a (3,) vector')
        self._translation = value
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
    def matrix(self):
        """(4,4) float : The homogenous transform matrix for this node.

        Note that this matrix's elements are not settable,
        it's just a copy of the internal matrix. You can set the whole
        matrix, but not an individual element.
        """
        if self._transform is None:
            self._transform = node_math.tqs2matrix(
                translation=self.translation,
                quaternion=self.rotation,
                scale=self.scale
            )
        return self._transform.copy()

    @matrix.setter
    def matrix(self, value):
        value = np.asanyarray(value)
        if value.shape != (4,4):
            raise ValueError('Matrix must be a 4x4 numpy ndarray')
        if not np.allclose(value[3,:], np.array([0.0, 0.0, 0.0, 1.0])):
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
    #                     Callback Functions
    # =========================================================================

    def render(self):
        pass

    def callback_immediate_mode_ui(self):
        pass

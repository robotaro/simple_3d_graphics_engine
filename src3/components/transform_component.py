import numpy as np
from src.core import constants

from src.math import mat4
from src2.components.component import Component


class TransformComponent:

    _type = "transform_3d"

    __slots__ = [
        "local_matrix",
        "world_matrix",
        "inverse_world_matrix",
        "position",
        "rotation",
        "scale",
        "use_degrees",
        "input_values_updated",
        "local_matrix_updated",
        "dirty"
    ]

    def __init__(self, position: tuple, rotation: tuple, scale: tuple, use_degrees=False):

        self.position = position
        self.rotation = rotation
        self.scale = scale

        if len(self.scale) == 1:
            self.scale = (self.scale[0], self.scale[0], self.scale[0])

        if len(self.scale) == 2:
            raise Exception("[ERROR] Input scale from parameters contains 2 values. Please make sure you have"
                            "either 1 or 3")

        self.use_degrees = use_degrees

        if self.use_degrees:
            self.rotation = (np.radians(self.rotation[0]),
                             np.radians(self.rotation[1]),
                             np.radians(self.rotation[2]))

        self.local_matrix = np.eye(4, dtype=np.float32)
        self.world_matrix = np.eye(4, dtype=np.float32)
        self.inverse_world_matrix = np.eye(4, dtype=np.float32)  # Doesn't get update correctly for some reason
        self.input_values_updated = True
        self.local_matrix_updated = False
        self.dirty = True

    def update(self) -> bool:
        """
        This function serverd multiple purposes. If "input_values_updated" is true, it will reconstruct
        the local matrix based on the translation, rotation (including mode) and scale values.
        If however, "local_matrix_updated" is true, it will update the input values to reflect what would
        be necessary to recreate said local matrix

        # IMPORTANT: Updating the local matrix TAKES PRECEDENCE. So if both input values are local matrix
                     are updated before the update function is called (both flags true) the local matrix
                     will remain unchanged and the input values will be updated instead

        :return: boolean, TRUE if the local matrix has been updated
        """

        if self.local_matrix_updated:
            self.position = tuple(self.local_matrix[:3, 3])
            self.rotation = tuple(mat4.to_euler_xyz(self.local_matrix))
            # TODO: Scale is missing!!!
            self.local_matrix_updated = False
            self.input_values_updated = False  # They have now been overwritten, so no updated required.
            self.dirty = True
            return True

        if self.input_values_updated:
            self.local_matrix = mat4.create_transform_euler_xyz(
                np.array(self.position, dtype=np.float32),
                np.array(self.rotation, dtype=np.float32),
                np.array(self.scale, dtype=np.float32),)
            self.input_values_updated = False
            self.dirty = True
            return True

        return False

    def move(self, delta_position: np.array):
        self.position += delta_position
        self.input_values_updated = True

    def rotate(self, delta_rotation: np.array):
        self.rotation += delta_rotation
        self.input_values_updated = True

    def set_position(self, position: tuple):
        self.position = position
        self.input_values_updated = True

    def set_rotation(self, position: tuple):
        self.position = position
        self.input_values_updated = True

    def draw_imgui_properties(self, imgui):

        imgui.text(f"Transform")
        a, self.position = imgui.drag_float3("Position", *self.position, constants.IMGUI_DRAG_FLOAT_PRECISION)
        b, self.rotation = imgui.drag_float3("Rotation", *self.rotation, constants.IMGUI_DRAG_FLOAT_PRECISION)
        c, self.scale = imgui.drag_float3("Scale", *self.scale, constants.IMGUI_DRAG_FLOAT_PRECISION)
        self.input_values_updated |= a | b | c
        imgui.spacing()

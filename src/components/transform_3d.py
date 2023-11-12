import numpy as np

from src.core import constants
from src.math import mat4
from src.components.component import Component


class Transform3D(Component):

    _type = "transform"

    __slots__ = [
        "local_matrix",
        "world_matrix",
        "position",
        "rotation",
        "scale",
        "degrees",
        "mode",
        "input_values_updated",
        "local_matrix_updated"
    ]

    def __init__(self, parameters, system_owned=False):
        super().__init__(parameters=parameters, system_owned=system_owned)

        self.position = Component.dict2tuple_float(input_dict=self.parameters,
                                                   key="position",
                                                   default_value=(0.0, 0.0, 0.0))

        self.rotation = Component.dict2tuple_float(input_dict=self.parameters,
                                                   key="rotation",
                                                   default_value=(0.0, 0.0, 0.0))

        self.scale = Component.dict2float(input_dict=self.parameters,
                                          key="scale",
                                          default_value=1.0)

        self.mode = Component.dict2string(input_dict=self.parameters,
                                          key="mode",
                                          default_value=constants.TRANSFORM_3D_MODE_NAME_EULER_XYZ)

        self.degrees = Component.dict2bool(input_dict=self.parameters,
                                           key="degrees",
                                           default_value=False)

        if self.degrees:
            self.rotation = (self.rotation[0] * constants.DEG2RAD,
                             self.rotation[1] * constants.DEG2RAD,
                             self.rotation[2] * constants.DEG2RAD)

        self.local_matrix = np.eye(4, dtype=np.float32)
        self.world_matrix = np.eye(4, dtype=np.float32)
        self.input_values_updated = True
        self.local_matrix_updated = False

    def update(self) -> None:
        """
        This function serverd multiple purposes. If "input_values_updated" is true, it will reconstruct
        the local matrix based on the translation, rotation (including mode) and scale values.
        If however, "local_matrix_updated" is true, it will update the input values to reflect what would
        be necessary to recreate said local matrix

        # IMPORTANT: Updating the local matrix TAKES PRECEDENCE. So if both input values are local matrix
                     are updated before the update function is called (both flags true) the local matrix
                     will remain unchanged and the input values will be updated instead

        :return: None
        """

        if self.local_matrix_updated:
            self.position = tuple(self.local_matrix[:3, 3])

            self.local_matrix_updated = False
            self.input_values_updated = False  # They have now been overwritten, so no updated required.
            return

        if self.input_values_updated:
            #self.local_matrix = mat4.compute_transform(position=self.position,
            #                                           rotation_rad=self.rotation,
            #                                           scale=self.scale)
            self.local_matrix = mat4.create_transform_euler_xyz(
                np.array(self.position, dtype=np.float32),
                np.array(self.rotation, dtype=np.float32),
                self.scale)
            self.input_values_updated = False
            return

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

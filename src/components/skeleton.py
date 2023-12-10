import pandas as pd
import numpy as np

from src.core import constants
from src.components.component import Component
from src.utilities import utils_urdf, utils_mjcf, utils_io

class Skeleton(Component):

    __slots__ = [
        "joints",
        "num_bones",
        "world_matrices",
        "local_matrices",

    ]

    _type = constants.COMPONENT_TYPE_ROBOT

    def __init__(self, parameters, system_owned=False):
        super().__init__(parameters=parameters, system_owned=system_owned)

        self.joints = None
        self.num_bones = Component.dict2int(input_dict=parameters, key="num_bones", default_value=1)
        matrix_shape = (self.num_bones, 4, 4)
        self.local_matrices = np.empty(matrix_shape, dtype=np.float32)
        self.world_matrices = np.empty(matrix_shape, dtype=np.float32)

    def initialise(self, **kwargs):


        pass

    def from_dataframe(self, skeleton_df: pd.DataFrame):

        num_bones = skeleton_df.index.size
        self.blueprint_df = skeleton_df
        self.parent_indices = np.array(skeleton_df[PARAMS_PARENT], dtype=np.int32)
        self.local_matrices = np.ndarray((num_bones, 4, 4), dtype=np.float32)
        self.world_matrices = np.ndarray((num_bones, 4, 4), dtype=np.float32)
        self.__ready = True

        for bone_index, bone in self.blueprint_df.iterrows():
            self.local_matrices[bone_index, :, :] = np.eye(4, dtype=np.float32)
            self.world_matrices[bone_index, :, :] = np.eye(4, dtype=np.float32)
            self.set_rotation(bone_index=bone_index)
            self.set_position(bone_index=bone_index,
                              x=bone[PARAMS_POS_X],
                              y=bone[PARAMS_POS_Y],
                              z=bone[PARAMS_POS_Z])

        self.update_world_matrices()

    def update_world_matrices(self, offset_root_matrix=None):
        """
        Re-calculates all world matrices based on their hierarchical local matrix allocation
        :param offset_root_matrix: you can offset the entire skeleton
        :return:
        """
        self.__check_if_ready()

        # Only update if something has changed
        if not self.dirty_flag:
            return

        if offset_root_matrix is not None:
            self.world_matrices[0] = offset_root_matrix * self.local_matrices[0]
        else:
            self.world_matrices[0] = self.local_matrices[0][:]

        num_bones = self.local_matrices.shape[0]
        for current_index in range(1, num_bones):
            parent_index = self.parent_indices[current_index]
            self.world_matrices[current_index] = self.world_matrices[parent_index] @ self.local_matrices[current_index]

    def __check_if_ready(self):
        if not self.__ready:
            raise Exception('[ERROR] Skeleton not yet generated from blueprint')

        # ========================================================
        #                   Setters and getters
        # ========================================================

    def set_rotation(self, bone_index, x=0.0, y=0.0, z=0.0, apply_offsets=True):
        self.__check_if_ready()
        order = self.blueprint_df.at[bone_index, PARAMS_ROTATION_ORDER]

        if apply_offsets:
            x = self.blueprint_df.at[bone_index, PARAMS_ANGLE_OFFSET_X] + x
            y = self.blueprint_df.at[bone_index, PARAMS_ANGLE_OFFSET_Y] + y
            z = self.blueprint_df.at[bone_index, PARAMS_ANGLE_OFFSET_Z] + z
        self.local_matrices[bone_index, :3, :3] = mat3.euler(x_rad=x, y_rad=y, z_rad=z, order=order)
        self.dirty_flag = True

    def set_position(self, bone_index, x=0.0, y=0.0, z=0.0):
        self.__check_if_ready()
        self.local_matrices[bone_index, :3, 3] = [x, y, z]
        self.dirty_flag = True

    def get_local_matrix(self, bone_index):
        self.__check_if_ready()
        return self.local_matrices[bone_index, :, :]

    def get_world_matrix(self, bone_index):
        self.__check_if_ready()
        return self.world_matrices[bone_index, :, :]

    def get_parent_index(self, bone_index):
        self.__check_if_ready()
        return self.parent_indices[bone_index]



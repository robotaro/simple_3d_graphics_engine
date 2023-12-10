import pandas as pd
import numpy as np

from src.core import constants
from src.components.component import Component
from src.math import mat4
from src.utilities import utils_urdf, utils_mjcf, utils_io


class Skeleton(Component):

    __slots__ = [
        "world_matrices",
        "local_matrices",
        "parent_indices",
        "children_indices",
        "num_children"
    ]

    _type = constants.COMPONENT_TYPE_ROBOT

    def __init__(self, parameters, system_owned=False):
        super().__init__(parameters=parameters, system_owned=system_owned)

        self.local_matrices = None
        self.world_matrices = None
        self.parent_indices = None
        self.children_indices = None
        self.num_children = None

    def initialise(self, **kwargs):

        resource_id = self.parameters.get(constants.COMPONENT_ARG_RESOURCE_ID, None)
        if resource_id is None:
            raise Exception(f"[ERROR] Skeleton component has no 'resource_id' argument defined")

        resource = kwargs["resource_manager"].resources.get(resource_id, None)
        if resource is None:
            raise Exception(f"[ERROR] No resource '{resource_id}' found in the resource manager")

        # Copy any relevant data from resource
        self.num_children = resource.data_blocks["num_children"].data.copy()
        self.children_indices = resource.data_blocks["children_indices"].data.copy()
        self.parent_indices = resource.data_blocks["parent_index"].data.copy()

        # Allocate memory for bone matrices
        num_bones = resource.data_blocks["parent_index"].data.size
        matrix_shape = (num_bones, 4, 4)
        self.local_matrices = np.empty(matrix_shape, dtype=np.float32)
        self.world_matrices = np.empty(matrix_shape, dtype=np.float32)

        # Calculate local matrices
        # TODO: [OPTIMIZE] I tried this in numba but it didn't like 2D slicing from a 3D matrix.
        for bone_index in range(num_bones):
            mat4.matrix_composition(
                resource.data_blocks["translation"].data[bone_index, :],
                resource.data_blocks["rotation"].data[bone_index, :],
                resource.data_blocks["scale"].data[bone_index, :],
                self.local_matrices[bone_index, :, :])

        # Calculate world matrices based on local matrices and their hierarchy
        self.update_world_matrices()

    def update_world_matrices(self, external_world_matrix=None):
        """
        Re-calculates all world matrices based on their hierarchical local matrix allocation
        :param offset_root_matrix: you can offset the entire skeleton
        :return:
        """

        if external_world_matrix is None:
            external_world_matrix = np.eye(4, dtype=np.float32)

        # First find the root node:
        root_nodes = [node_index for node_index, parent_index in enumerate(self.parent_indices) if parent_index == -1]
        if len(root_nodes) == 0:
            raise Exception("[ERROR] No root node (one with parent_index equals -1) was found")

        next_node_indices = root_nodes

        while len(next_node_indices) > 0:

            current_node_index = next_node_indices.pop()
            parent_index = self.parent_indices[current_node_index]
            children_indices = [self.children_indices[current_node_index, sub_index]
                                for sub_index in range(self.num_children[current_node_index])]

            #print(f" - Node {current_node_index} : parent {parent_index} : children {children_indices}")

            if parent_index == -1:
                parent_matrix = external_world_matrix
            else:
                parent_matrix = self.world_matrices[parent_index, :, :]

            self.world_matrices[current_node_index, :, :] = parent_matrix @ self.local_matrices[current_node_index, :, :]
            next_node_indices.extend(children_indices)

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



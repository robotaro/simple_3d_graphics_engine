import numpy as np
import moderngl


from src.math import mat4
from src.core import constants
from src.core.component import Component


class MultiTransform3D(Component):

    _type = "transform"

    __slots__ = [
        "local_matrices",
        "world_matrices",
        "dirty"
    ]

    def __init__(self, parameters, system_owned=False):
        super().__init__(parameters=parameters, system_owned=system_owned)
        self.local_matrices = None
        self.world_matrices = None
        self.dirty = False

    def initialise(self, **kwargs):

        data_manager = kwargs[constants.MODULE_NAME_DATA_MANAGER]
        resource_id = self.parameters.get(constants.COMPONENT_ARG_RESOURCE_ID, None)

        if resource_id is None:
            return

        nodes_data_group = data_manager.data_groups[resource_id]

        # Copy any relevant data from resource
        num_children = nodes_data_group.data_blocks["num_children"].data.copy()
        children_indices = nodes_data_group.data_blocks["children_indices"].data.copy()
        parent_indices = nodes_data_group.data_blocks["parent_index"].data.copy()

        # Allocate memory for bone matrices
        num_bones = nodes_data_group.data_blocks["parent_index"].data.size
        matrix_shape = (num_bones, 4, 4)
        local_matrices = np.empty(matrix_shape, dtype=np.float32)
        self.local_matrices = np.empty(matrix_shape, dtype=np.float32)
        self.world_matrices = np.empty(matrix_shape, dtype=np.float32)

        # Calculate local matrices
        for bone_index in range(num_bones):
            mat4.matrix_composition(
                nodes_data_group.data_blocks["translation"].data[bone_index, :],
                nodes_data_group.data_blocks["rotation"].data[bone_index, :],
                nodes_data_group.data_blocks["scale"].data[bone_index, :],
                local_matrices[bone_index, :, :])

        # First find the root node:
        root_nodes = [node_index for node_index, parent_index in enumerate(parent_indices) if parent_index == -1]
        if len(root_nodes) == 0:
            raise Exception("[ERROR] No root node (one with parent_index equals -1) was found")

        next_node_indices = root_nodes

        while len(next_node_indices) > 0:

            current_node_index = next_node_indices.pop()
            parent_index = parent_indices[current_node_index]
            updated_children_indices = [children_indices[current_node_index, sub_index]
                                for sub_index in range(num_children[current_node_index])]

            if parent_index == -1:
                parent_matrix = np.eye(4, dtype=np.float32)
            else:
                parent_matrix = self.local_matrices[parent_index, :, :]

            self.local_matrices[current_node_index, :, :] = parent_matrix @ local_matrices[current_node_index, :, :]
            next_node_indices.extend(updated_children_indices)

        self.dirty = True

    def upload_world_matrix_to_ubo(self, ubo: moderngl.UniformBlock):

        if not self.dirty:
            return

        # Write the data to the UBO
        ubo.write(self.world_matrices.tobytes(), offset=0)
        self.dirty = False

    def get_num_transforms(self) -> int:
        if self.world_matrices is None:
            return None

        return self.world_matrices.shape[0]

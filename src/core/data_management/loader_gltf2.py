import numpy as np

from src.utilities import utils_gltf
from src.core.data_block import DataBlock
from src.core import constants


class LoaderGLTF2:

    def __init__(self):
        pass

    def load(self, gltf_fpath: str) -> dict:

        """
        WARNING! This function is not completed!!!
        :param gltf_fpath:
        :return:
        """

        new_resource = {}
        header, data, _ = utils_gltf.load_gltf_parts(gltf_fpath=gltf_fpath)
        accessor_arrays = utils_gltf.extract_accessor_arrays(header=header, data=data)
        meshes = utils_gltf.load_meshes(header=header, accessor_arrays=accessor_arrays)


        return new_resource


    def load_nodes(self, header: dict) -> dict:

        nodes = header[GLTF_NODE]
        num_nodes = len(nodes)

        if num_nodes == 0:
            return []

        rotation = DataBlock(data_shape=(num_nodes, 4),
                             data_type=np.float32,
                             data_format=constants.DATA_BLOCK_FORMAT_ROTATION_QUAT)

        position = DataBlock(data_shape=(num_nodes, 3),
                             data_type=np.float32,
                             data_format=constants.DATA_BLOCK_FORMAT_ROTATION_QUAT)

        scale = DataBlock(data_shape=(num_nodes, 3),
                          data_type=np.float32,
                          data_format=constants.DATA_BLOCK_FORMAT_SCALE3)

        transform = DataBlock(data_shape=(num_nodes, 4, 4),
                              data_type=np.float32,
                              data_format=constants.DATA_BLOCK_FORMAT_TRANSFORM44)

        children_nodes_list = []
        max_num_children = -1

        for index, node in enumerate(nodes):

            # Special case for "children" as they need to post-processed into their own array
            children = node.get(GLTF_CHILDREN, [])
            children_nodes_list.append(children)
            max_num_children = len(children) if len(children) > max_num_children else max_num_children

            if GLTF_ROTATION in node:
                rotation.data[index, :] = node[GLTF_ROTATION]

            if GLTF_TRANSLATION in node:
                position.data[index, :] = node[GLTF_TRANSLATION]

            if GLTF_SCALE in node:
                scale.data[index, :] = node[GLTF_SCALE]

            if GLTF_MATRIX in node:
                transform.data[index, :] = np.array(node[GLTF_MATRIX], dtype=np.float32).reshape(4, 4).T

        # Populate children index array
        children = DataBlock(data_shape=(num_nodes, max_num_children),
                             data_type=np.int32,
                             data_format=constants.DATA_BLOCK_FORMAT_TRANSFORM44)
        children.data[:] = -1  # -1 indicates invalid indices

        # TODO: Refactor this to use a DAG! It will require one extra levl of indirection, but once converted... PROFIT!
        for index, children_indices in enumerate(children_nodes_list):
            current_num_children = len(children_indices)
            if current_num_children == 0:
                continue
            children.data[index, :current_num_children] = children_indices

        return {
            "position": position,
            "rotation": rotation,
            "scale": scale,
            "transform": transform,
            "children": children
        }

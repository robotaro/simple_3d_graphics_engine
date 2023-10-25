import json
import numpy as np
import os

import pygltflib
from src.core.data_management.data_block import DataBlock
from src.core import constants

# Constants
GLTF_MESHES = "meshes"
GLTF_NODE = "nodes"
GLTF_ROTATION = "rotation"
GLTF_TRANSLATION = "translation"
GLTF_SCALE = "scale"
GLTF_MATRIX = "matrix"
GLTF_SKIN = "skin"
GLTF_CHILDREN = "children"
GLTF_BUFFERS = "buffers"
GLTF_BYTE_LENGTH = "byteLength"
GLTF_URI = "uri"


class LoaderGLTF2:

    def __init__(self):


        pass

    def load(self, fpath) -> dict:

        file_directory = os.path.dirname(fpath)
        filename = os.path.basename(fpath)
        _, extension = os.path.splitext(filename)

        # Load GLTF header data
        gltf_header = None
        if extension == ".gltf":
            with open(fpath, "r") as file:
                gltf_header = json.load(file)

        if extension == ".glb":
            raise NotImplemented("[ERROR] Unified .glb files (JSON + binnary dta) not yet supported")

        # ====== DEBUG =======
        gltf_data_3rd_party = pygltflib.GLTF2().load(fname=fpath)
        for node in gltf_data_3rd_party.nodes:
            print(node)

        new_resource = {}

        # Load binary data
        current_dir = os.path.dirname(fpath)
        bin_fpath = os.path.join(current_dir, gltf_header[GLTF_BUFFERS][0][GLTF_URI])
        target_bin_data_size = gltf_header[GLTF_BUFFERS][0][GLTF_BYTE_LENGTH]

        gltf_data = None
        with open(bin_fpath, "rb") as file:
            gltf_data = file.read()

            if target_bin_data_size != len(gltf_data):
                raise Exception(f"[ERROR] Loaded GLTF binary data from {bin_fpath} has {len(gltf_data)} bytes, "
                                f"but was expected to have {target_bin_data_size} bytes")

        meshes_dict = self._load_meshes(header=gltf_header, data=gltf_data)
        node_dict = self._load_nodes(header=gltf_header)



        return new_resource

    def _load_meshes(self, header: dict, data: bytes) -> dict:

        meshes = header.get(GLTF_MESHES, None)
        if meshes is None:
            return {}




        g = 0




    def _load_nodes(self, header: dict) -> dict:

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





import json
import numpy as np
import os

from pygltflib import GLTF2, BufferFormat
from src.core.data_management.data_block import DataBlock
from src.core import constants

# Constants
GLTF_MESHES = "meshes"
GLTF_PRIMITIVES = "primitives"
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
GLTF_ACCESSORS = "accessors"
GLTF_BUFFER_VIEWS = "bufferViews"


class LoaderGLTF2:

    def __init__(self):
        pass

    def load_glb(self, glb_fpath: str):

        glb = GLTF2().load_binary(glb_fpath)
        something = glb.convert_buffers(BufferFormat.DATAURI)
        g = 0

    def load_gltf(self, gltf_fpath) -> dict:

        """
        WARNING! This function is not completed!!!
        :param gltf_fpath:
        :return:
        """

        file_directory = os.path.dirname(gltf_fpath)
        filename = os.path.basename(gltf_fpath)
        _, extension = os.path.splitext(filename)

        # Load GLTF header data
        gltf_header = None
        if extension == ".gltf":
            with open(gltf_fpath, "r") as file:
                gltf_header = json.load(file)

        if extension == ".glb":
            raise NotImplemented("[ERROR] Unified .glb files (JSON + binnary dta) not yet supported")

        new_resource = {}

        # Load binary data
        current_dir = os.path.dirname(gltf_fpath)
        bin_fpath = os.path.join(current_dir, gltf_header[GLTF_BUFFERS][0][GLTF_URI])
        target_bin_data_size = gltf_header[GLTF_BUFFERS][0][GLTF_BYTE_LENGTH]

        gltf_data = None
        with open(bin_fpath, "rb") as file:
            gltf_data = file.read()

            if target_bin_data_size != len(gltf_data):
                raise Exception(f"[ERROR] Loaded GLTF binary data from {bin_fpath} has {len(gltf_data)} bytes, "
                                f"but was expected to have {target_bin_data_size} bytes")

        accessors_data_list = self.load_accessor_data(header=gltf_header, data=gltf_data)
        meshes_dict = self.load_meshes(header=gltf_header, accessors_data_list=accessors_data_list)
        node_dict = self.load_nodes(header=gltf_header)
        g = 0



        return new_resource

    def load_meshes(self, header: dict, accessors_data_list: list) -> dict:

        rendering_modes = {
            0: "points",
            1: "lines",
            2: "line_loop",
            3: "line_strip",
            4: "triangles",
            5: "triangle_strip",
            6: "triangle_fan"
        }

        meshes = header[GLTF_MESHES]
        meshes_final = []
        for mesh in meshes:

            primitives = mesh[GLTF_PRIMITIVES]
            primitives_final = []
            for primitive_index, primitive in enumerate(primitives):

                primitives_final.append(
                    {
                        "attributes": {key: accessors_data_list[index]
                                       for index, (key, index) in enumerate(primitive["attributes"].items())},
                        "material": primitive["material"],
                        "indices": accessors_data_list[primitive["indices"]],
                        "rendering_mode": rendering_modes[primitive["mode"]]
                    })

            meshes_final.append({
                "name": mesh["name"],
                "primitives": primitives_final})


    def load_accessor_data(self, header: dict, data: bytes) -> list:


        # Split input data into their respective buffer views to make it easy to be loaded by the accessors
        buffer_views_data = [self.load_buffer_view_data(buffer_view=buffer_view, data=data)
                             for buffer_view in header[GLTF_BUFFER_VIEWS]]

        data_type_map = {
          5120: np.int8,
          5121: np.uint8,
          5122: np.int16,
          5123: np.uint16,
          5124: np.int32,
          5125: np.uint32,
          5126: np.float32}

        data_shape_map = {
            "SCALAR": (1,),
            "VEC2": (2,),
            "VEC3": (3,),
            "VEC4": (4,),
            "MAT2": (2, 2),
            "MAT3": (3, 3),
            "MAT4": (4, 4)}

        data_format_size_map = {
            "SCALAR": 1,
            "VEC2": 2,
            "VEC3": 3,
            "VEC4": 4,
            "MAT2": 4,
            "MAT3": 9,
            "MAT4": 16}

        accessors_arrays = []

        for accessor in header[GLTF_ACCESSORS]:

            buffer_data = buffer_views_data[accessor["bufferView"]]

            accessor_offset = accessor["byteOffset"]
            data_shape = data_shape_map[accessor["type"]]
            data_type = data_type_map[accessor["componentType"]]
            data_format_size = data_format_size_map[accessor["type"]]
            num_elements = accessor["count"]

            acessor_data = np.frombuffer(offset=accessor_offset,
                                         count=num_elements * data_format_size,
                                         dtype=data_type,
                                         buffer=buffer_data)

            accessor_array = acessor_data.reshape((-1, *data_shape)) if accessor["type"] != "SCALAR" else acessor_data

            accessors_arrays.append(accessor_array)

        return accessors_arrays

    def load_buffer_view_data(self, buffer_view: dict, data: bytes) -> bytes:

        # Extract buffer view properties
        byte_offset = buffer_view.get("byteOffset", 0)
        byte_length = buffer_view["byteLength"]
        byte_stride = buffer_view.get("byteStride", 0)  # Optional

        # Calculate the starting and ending byte positions in the binary data
        last_byte = byte_offset + byte_length

        if byte_stride == 0:
            # If byteStride is not specified, read all the data in one go
            loaded_data = data[byte_offset:last_byte]
        else:
            # If byteStride is specified, read data element by element
            num_elements = byte_length // byte_stride
            loaded_data = b''.join(data[byte_offset + i * byte_stride:byte_offset + (i + 1) * byte_stride]
                                    for i in range(num_elements))


        return loaded_data

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

import os
import json
import struct
import numpy as np

# DEBUG
import matplotlib.pyplot as plt

# Constants
GLTF_MESHES = "meshes"
GLTF_PRIMITIVES = "primitives"
GLTF_NODES = "nodes"
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

GLTF_ATTR_POSITION = "POSITION"
GLTF_ATTR_NORMAL = "NORMAL"
GLTF_ATTR_TANGENT = "TANGENT"

GLTF_COMPONENT_TYPE_MAP = {
      5120: np.int8,
      5121: np.uint8,
      5122: np.int16,
      5123: np.uint16,
      5124: np.int32,
      5125: np.uint32,
      5126: np.float32}

GLTF_DATA_SHAPE_MAP = {
    "SCALAR": (1,),
    "VEC2": (2,),
    "VEC3": (3,),
    "VEC4": (4,),
    "MAT2": (2, 2),
    "MAT3": (3, 3),
    "MAT4": (4, 4)}

GLTF_DATA_NUM_ELEMENTS_MAP = {
    "SCALAR": 1,
    "VEC2": 2,
    "VEC3": 3,
    "VEC4": 4,
    "MAT2": 4,
    "MAT3": 9,
    "MAT4": 16}

GLTF_ANIMATION_PATH_MAP = {
    "translation": 0,
    "rotation": 1,
    "scale": 2}

GLTF_INTERPOLATION_MAP = {
    "LINEAR": 0,
    "STEP": 1,
    "CUBICSPLINE": 2}

PRIMITIVE_RENDERING_MODES = {
    0: "points",
    1: "lines",
    2: "line_loop",
    3: "line_strip",
    4: "triangles",
    5: "triangle_strip",
    6: "triangle_fan"
}


class GLTFReader:

    __slots__ =[
        "gltf_header",
        "gltf_buffer_view_data",
        "gltf_dependencies",
        "scenes"
    ]

    def __init__(self):
        self.gltf_header = None
        self.gltf_buffer_view_data = []
        self.gltf_dependencies = None
        self.scenes = []

    def load(self, gltf_fpath: str):

        """
        Loads the header and binary information form the GLTF file. Currently, it assumes there is only
        ONE scene. If there are more the one scene it will throw an error
        :param gltf_fpath: str, absolute path to the input GLTF file
        :return:
        """

        # Then, read it in my own way
        filename = os.path.basename(gltf_fpath)
        _, extension = os.path.splitext(filename)

        if extension == ".gltf":
            self.__load_gltf(fpath=gltf_fpath)

        if extension == ".glb":
            self.__load_glb(fpath=gltf_fpath)

        # Load dependencies
        # TODO: Load any textures that are listed in the gltf_header


    def __load_gltf(self, fpath) -> None:

        # Load Header
        with open(fpath, "r") as file:
            self.gltf_header = json.load(file)

            # Make sure we only have one scene
            if len(self.gltf_header["scenes"]) > 1:
                raise ValueError("[ERROR] Only one scene per GLTF is supported")

        # Load binary data
        gltf_dir = os.path.dirname(fpath)
        bin_fpath = os.path.join(gltf_dir, self.gltf_header[GLTF_BUFFERS][0][GLTF_URI])
        target_bin_data_size = self.gltf_header[GLTF_BUFFERS][0][GLTF_BYTE_LENGTH]

        # read and process binary data
        with open(bin_fpath, "rb") as file:

            self.__process_binary_data(binary_data=file.read())

    def __load_glb(self, fpath):

        with open(fpath, 'rb') as file:

            # Read binary file header
            magic, version, length = struct.unpack('<4sII', file.read(12))

            if magic != b'glTF':
                raise ValueError('File is not a valid GLB format')

            # Read the GLTF header
            chunk_length, chunk_type = struct.unpack('<II', file.read(8))
            if chunk_type != 0x4E4F534A:
                raise ValueError('Expected a JSON chunk')

            self.gltf_header = json.loads(file.read(chunk_length))

            # Read the binary chunk header (if any)
            chunk_length, chunk_type = struct.unpack('<II', file.read(8))
            if chunk_type != 0x004E4942:
                raise ValueError('Expected a BIN chunk')

            # Read and process the binary data
            self.__process_binary_data(binary_data=file.read(chunk_length))

    def __process_binary_data(self, binary_data: bytes) -> None:
        self.gltf_buffer_view_data = [self.select_data_using_buffer_view(buffer_view=buffer_view,
                                                                         gltf_data=binary_data)
                                      for buffer_view in self.gltf_header[GLTF_BUFFER_VIEWS]]
        g = 0

    def get_accessor(self, index: int):

        if self.gltf_header is None:
            return None

        return self.gltf_header["accessors"][index]

    def get_data(self, accessor: dict, validate_data=True):
        """
        This function reads the parts of the binary array in memory (loaded from the .bin file) and re-interprets
        the raw bytes into numpy arrays according to the accessor's specified data parameters.
        :param accessor: dict, loaded directly from the GLTF file
        :return:
        """

        if self.gltf_header is None:
            return None

        buffer_view_data = self.gltf_buffer_view_data[accessor["bufferView"]]
        accessor_offset = accessor.get("byteOffset", 0)
        data_shape = GLTF_DATA_SHAPE_MAP[accessor["type"]]
        data_type = GLTF_COMPONENT_TYPE_MAP[accessor["componentType"]]
        data_format_size = GLTF_DATA_NUM_ELEMENTS_MAP[accessor["type"]]
        num_elements = accessor["count"]

        data = np.frombuffer(buffer=buffer_view_data,
                             offset=accessor_offset,
                             count=num_elements * data_format_size,
                             dtype=data_type)

        data = data.reshape((-1, *data_shape)) if accessor["type"] != "SCALAR" else data

        if validate_data and "min" in accessor and "max" in accessor:
            target_data_min = np.array(accessor["min"], dtype=data_type)
            target_data_max = np.array(accessor["max"], dtype=data_type)

            data_min = np.min(data, axis=0).flatten()
            data_max = np.max(data, axis=0).flatten()

            if not np.isclose(target_data_min, data_min).all():
                print(f"[WARNING] Minimum values differ from loaded ones for accessor {accessor}")

            if not np.isclose(target_data_max, data_max).all():
                print(f"[WARNING] Maximum values differ from loaded ones for accessor {accessor}")

        if accessor["type"] in ["MAT2", "MAT3", "MAT4"]:
            # Transposing is required for the matrix as they are laid ou COLUMN-MAJOR in bytes, but stored
            # as ROW-MAJOR in the numpy arrays
            data_reshaped = np.transpose(data, (0, 2, 1))

        return data

    def select_data_using_buffer_view(self, buffer_view: dict, gltf_data: bytes) -> bytes:

        """
        Returns a CONTIGUOUS data array that you can then use your np.frombuffer to extrac the data you need
        :param buffer_view:
        :param data:
        :return:
        """

        # Extract buffer view properties
        byte_offset = buffer_view.get("byteOffset", 0)
        byte_length = buffer_view["byteLength"]
        byte_stride = buffer_view.get("byteStride", 0)  # Optional

        # Calculate the starting and ending byte positions in the binary data
        last_byte = byte_offset + byte_length

        if byte_stride == 0:
            # If byteStride is not specified, read all the data in one go
            loaded_data = gltf_data[byte_offset:last_byte]
        else:
            # If byteStride is specified, read data element by element
            num_elements = byte_length // byte_stride
            loaded_data = b''.join(gltf_data[byte_offset + i * byte_stride:byte_offset + (i + 1) * byte_stride]
                                   for i in range(num_elements))

        return loaded_data

    def get_material(self, index: int):

        if self.gltf_header is None:
            return None

        return self.gltf_header["materials"][index]

    def get_animation(self, index: int):

        if self.gltf_header is None:
            return None

        animation_header = self.gltf_header["animations"][index]
        all_input_accessors = []
        channels = {"translation": [], "rotation": [], "scale": []}

        # Animation channels
        for channel in animation_header["channels"]:

            sampler = animation_header["samplers"][channel["sampler"]]
            output_accessor = self.gltf_header["accessors"][sampler["output"]]
            channels[channel["target"]["path"]].append(
                {"node_index": channel["target"]["node"],
                 "animation_data": self.get_data(accessor=output_accessor)})

            all_input_accessors.append(self.gltf_header["accessors"][sampler["input"]])

        # Make sure that all animation channels use the same timeline, and if so, only return one
        unique_input_buffer_views = set([accessor["bufferView"] for accessor in all_input_accessors])
        if len(unique_input_buffer_views) != 1:
            raise Exception(f"All animation channels should be taking their timestamps from the same buffer view, "
                            f"and there are {len(unique_input_buffer_views)} sources instead.")

        timestamps = self.get_data(accessor=all_input_accessors[0])

        return channels, timestamps

    def get_nodes(self) -> dict:

        if self.gltf_header is None:
            return None

        # GPT 4
        nodes = []
        for node in self.gltf_header["nodes"]:
            node_data = {
                'name': node.get('name', None),
                'translation': np.array(node.get('translation', [0, 0, 0])),
                'rotation': np.array(node.get('rotation', [0, 0, 0, 1])),
                'scale': np.array(node.get('scale', [1, 1, 1])),
                'matrix': np.array(node.get('matrix', np.eye(4))),
                'children': node.get('children', []),
                'mesh': node.get('mesh', None),
                'skin': node.get('skin', None)
            }
            nodes.append(node_data)

        # Mine
        num_nodes = len(self.gltf_header[GLTF_NODES])
        node_name = []
        node_parent_index = np.ones((num_nodes,), dtype=np.int32) * -1
        node_matrix = np.empty((num_nodes, 4, 4), dtype=np.float32)
        node_translation = np.empty((num_nodes, 3), dtype=np.float32)
        node_rotation_quat = np.empty((num_nodes, 4), dtype=np.float32)
        node_scale = np.empty((num_nodes, 3), dtype=np.float32)

        for current_index, node in enumerate(self.gltf_header[GLTF_NODES]):

            for child_index in node.get("children", []):
                node_parent_index[child_index] = current_index

            node_matrix[current_index, :, :] = np.eye(4, dtype=np.float32)
            if "name" in node:
                # GLTF matrices are COLUMN-MAJOR, hence the transpose at the end
                node_name.append(node["name"])

            if "matrix" in node:
                # GLTF matrices are COLUMN-MAJOR, hence the transpose at the end
                node_matrix[current_index, :, :] = np.reshape(np.array(node["matrix"]), (4, 4)).T

            if "translation" in node:
                node_translation[current_index, :] = np.array(node["translation"])

            if "rotation" in node:
                node_rotation_quat[current_index, :] = np.array(node["rotation"])

            if "scale" in node:
                node_scale[current_index, :] = np.array(node["scale"])

        # TODO: Complete this
        return {

        }

    def get_all_meshes(self) -> list:
        if self.gltf_header is None:
            return None

        meshes = []
        for mesh in self.gltf_header["meshes"]:

            unique_primitive_render_modes = set([primitive["mode"] for primitive in mesh["primitives"]])
            if len(unique_primitive_render_modes) > 1:
                raise Exception(f"[ERROR] There are a mix of render modes between primitives. "
                                f"There should be only one: {[PRIMITIVE_RENDERING_MODES[value] for value in unique_primitive_render_modes]}")

            new_mesh = {
                "indices": [],
                "render_mode": PRIMITIVE_RENDERING_MODES[list(unique_primitive_render_modes)[0]],
                "attributes": {}}

            sum_num_vertices = 0

            # Combine all primitives into one single mesh
            for primitive in mesh["primitives"]:

                # Get data in right formate from primitive
                primitive_indices = self.get_data(accessor=self.get_accessor(primitive["indices"]))

                # Create new keys in current buffer with
                for attr_key in primitive["attributes"].keys():
                    # TODO: Consider what would happen if one primitive has a new attribute.
                    #       I think this would screw up the indices
                    new_mesh["attributes"][attr_key] = new_mesh["attributes"].get(attr_key, [])

                # Append new vertices, normals etc to current list, but indices must be shifted because we'll
                # concatenating primitives at the end
                new_mesh["indices"].append(primitive_indices + sum_num_vertices)
                for attr_key, accessor_index in primitive["attributes"].items():
                    data = self.get_data(accessor=self.get_accessor(accessor_index))
                    new_mesh["attributes"][attr_key].append(data)
                    if attr_key == "POSITION":
                        sum_num_vertices += data.shape[0] # Update the primitive index offset of this attribute is vertices

            # Concatenate all the meshes internal arrays into one per attribute
            new_mesh["indices"] = np.concatenate(new_mesh["indices"])
            for attr_key, attr_value in new_mesh["attributes"].items():
                new_mesh["attributes"][attr_key] = np.concatenate(attr_value, axis=0)

            meshes.append(new_mesh)

        return meshes

    def get_all_materials(self):
        return self.gltf_header["materials"]

    def get_skins(self):
        if self.gltf_header is None:
            return None

        skins = []
        for skin in self.gltf_header["skins"]:
            joints = skin["joints"]
            inverse_bind_matrices_accessor = self.gltf_header["accessors"][skin["inverseBindMatrices"]]
            inverse_bind_matrices_data = self.get_data(accessor=inverse_bind_matrices_accessor)

            # Convert to a suitable format, e.g., 4x4 matrices
            inverse_bind_matrices = inverse_bind_matrices_data.reshape((-1, 4, 4))

            skin_data = {
                'joints': joints,
                'inverseBindMatrices': inverse_bind_matrices
            }
            skins.append(skin_data)

        return skins

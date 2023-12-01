import os
import logging
from typing import Union
import numpy as np

# Specifuc libraries for certain extensions
import trimesh
from pygltflib import GLTF2

from src.core import constants
from src.core.data_block import DataBlock

from src.utilities import utils_obj, utils_bvh_reader, utils_gltf


class Resource:

    __slots__ = [
        "resource_type",
        "data_blocks"
    ]

    def __init__(self, resource_type: str):
        self.resource_type = resource_type
        self.data_blocks = {}


class ResourceManager:

    __slots__ = [
        "logger",
        "resources",
        "extension_handlers"
    ]

    def __init__(self, logger: logging.Logger):

        self.logger = logger
        self.resources = {}
        self.extension_handlers = {
            "obj": self.load_obj,
            "bvh": self.load_bvh,
            "gltf": self.load_gltf,
            "glb": self.load_gltf
        }

    def load(self, resource_uid: str, fpath: str):

        _, extension = os.path.splitext(fpath)
        extension_no_dot = extension.strip(".")

        handler = self.extension_handlers.get(extension_no_dot, None)
        if handler is None:
            self.logger.error(f"Extension '{extension}' not currently supported")
            return

        # Execute main loading operation here
        handler(resource_uid, fpath)

    def create_mesh_resource(self,
                             resource_uid: str,
                             vertices: np.ndarray,
                             normals: np.ndarray,
                             faces: np.ndarray,
                             uvs: Union[np.ndarray, None]):

        new_resource = Resource(resource_type=constants.RESOURCE_TYPE_MESH)

        new_resource.data_blocks["vertices"] = DataBlock(
            data_shape=vertices.shape,
            data_type=np.float32,
            data_format=constants.DATA_BLOCK_FORMAT_VEC3)
        new_resource.data_blocks["vertices"].data[:] = vertices

        new_resource.data_blocks["normals"] = DataBlock(
            data_shape=normals.shape,
            data_type=np.float32,
            data_format=constants.DATA_BLOCK_FORMAT_VEC3)
        new_resource.data_blocks["normals"].data[:] = normals

        new_resource.data_blocks["faces"] = DataBlock(
            data_shape=faces.shape,
            data_type=np.int32,
            data_format=constants.DATA_BLOCK_FORMAT_VEC3)
        new_resource.data_blocks["faces"].data[:] = faces

        if uvs is not None:
            new_resource.data_blocks["uv"] = DataBlock(
                data_shape=uvs.shape,
                data_type=np.float32,
                data_format=constants.DATA_BLOCK_FORMAT_VEC2)
            new_resource.data_blocks["uv"].data[:] = uvs

        self.resources[resource_uid] = new_resource

    def load_obj(self, resource_uid: str, fpath: str) -> None:

        mesh = trimesh.load(fpath)

        uvs = mesh.visual.uv if "uv" in mesh.visual.__dict__ else None

        self.create_mesh_resource(resource_uid=resource_uid,
                                  vertices=mesh.vertices,
                                  normals=mesh.vertex_normals,
                                  faces=mesh.faces,
                                  uvs=uvs)

    def load_bvh(self, resource_uid: str, fpath: str):

        bvh_reader = utils_bvh_reader.BVHReader()
        skeleton_df, animation_df, frame_period = bvh_reader.load(fpath=fpath)
        num_bones = skeleton_df.index.size
        bone_names = skeleton_df["name"].tolist()
        animation_columns = animation_df.columns.tolist()

        new_resource = Resource(resource_type=constants.RESOURCE_TYPE_MESH)

        # =========================[ Skeleton ]=========================

        # Parent Index
        new_resource.data_blocks["parent_index"] = DataBlock(
            data_shape=(num_bones,),
            data_type=np.int32,
            data_format=constants.DATA_BLOCK_FORMAT_ARRAY)
        new_resource.data_blocks["parent_index"].data[:] = skeleton_df["parent"].values
        new_resource.data_blocks["parent_index"].metadata["bone_names"] = bone_names

        # Bone Position Offset
        new_resource.data_blocks["position_offset"] = DataBlock(
            data_shape=(num_bones, 3),
            data_type=np.float32,
            data_format=constants.DATA_BLOCK_FORMAT_VEC3)
        new_resource.data_blocks["position_offset"].data[:] = skeleton_df[
            ["position_x", "position_y", "position_z"]].values

        # Bone Rotation Offset
        new_resource.data_blocks["rotation_offset"] = DataBlock(
            data_shape=(num_bones, 3),
            data_type=np.float32,
            data_format=constants.DATA_BLOCK_FORMAT_VEC3)
        new_resource.data_blocks["rotation_offset"].data[:] = skeleton_df[
            ["angle_offset_x", "angle_offset_y", "angle_offset_z"]].values

        # Bone Length
        new_resource.data_blocks["length"] = DataBlock(
            data_shape=(num_bones, ),
            data_type=np.float32,
            data_format=constants.DATA_BLOCK_FORMAT_ARRAY)
        new_resource.data_blocks["length"].data[:] = skeleton_df["length"].values

        # Bone Rotation Order
        new_resource.data_blocks["rotation_order"] = DataBlock(
            data_shape=(num_bones,),
            data_type=np.int32,
            data_format=constants.DATA_BLOCK_FORMAT_ARRAY)
        vectorized_conversion = np.vectorize(constants.RESOURCE_BVH_ROTATION_ORDER_MAP.get)
        rotation_order_integers = vectorized_conversion(skeleton_df["rotation_order"].values)
        new_resource.data_blocks["rotation_order"].data[:] = rotation_order_integers

        # =========================[ Animation ]=========================
        num_frames = animation_df.index.size

        # Position Animation (if any)
        new_shape = (num_frames, num_bones, 3)
        new_position_datablock = DataBlock(
            data_shape=new_shape,
            data_type=np.float32,
            data_format=constants.DATA_BLOCK_FORMAT_VEC3)
        new_position_datablock.data[:] = 0
        new_position_datablock.metadata["frame_period"] = frame_period

        # Rotation Animation
        new_rotation_datablock = DataBlock(
            data_shape=new_shape,
            data_type=np.float32,
            data_format=constants.DATA_BLOCK_FORMAT_VEC3)
        new_rotation_datablock.data[:] = 0
        new_rotation_datablock.metadata["frame_period"] = frame_period

        # Sort all position-related animation data according to the order of the bones in the skeleton
        for current_bone_index, current_bone_name in enumerate(bone_names):

            related_columns = [name for name in animation_columns if current_bone_name in name]
            for column_name in related_columns:

                if column_name.endswith("pos_x"):
                    new_position_datablock.data[:, current_bone_index, 0] = animation_df[column_name]

                if column_name.endswith("pos_y"):
                    new_position_datablock.data[:, current_bone_index, 1] = animation_df[column_name]

                if column_name.endswith("pos_z"):
                    new_position_datablock.data[:, current_bone_index, 2] = animation_df[column_name]

                if column_name.endswith("rot_x"):
                    new_rotation_datablock.data[:, current_bone_index, 0] = animation_df[column_name]

                if column_name.endswith("rot_y"):
                    new_rotation_datablock.data[:, current_bone_index, 1] = animation_df[column_name]

                if column_name.endswith("rot_z"):
                    new_rotation_datablock.data[:, current_bone_index, 2] = animation_df[column_name]

        new_resource.data_blocks["animation_position"] = new_position_datablock
        new_resource.data_blocks["animation_rotation"] = new_rotation_datablock

        self.resources[resource_uid] = new_resource

    def load_gltf(self, resource_uid: str, fpath: str) -> None:

        """
        This function operates a little differently form other resource loading funcitons. Given that the
        GLTF standard can hold many different types of data, each type of data is loaded as a separate
        resource. For example, each mesh will be its own MESH resource, node animation will be a SKELETON resource,
        etc. All resources will be named under the provide resource_uid group like "provided_uid/NEW_RESOURCE"
        :param resource_uid: string, unique identified for all ersources
        :param fpath:
        :return: None
        """

        directory = os.path.dirname(fpath)

        # Mapping GLTF component types to NumPy data types
        COMPONENT_TYPE_TO_NUMPY = {
            5120: np.int8,  # BYTE
            5121: np.uint8,  # UNSIGNED_BYTE
            5122: np.int16,  # SHORT
            5123: np.uint16,  # UNSIGNED_SHORT
            5125: np.uint32,  # UNSIGNED_INT
            5126: np.float32  # FLOAT
        }

        # Function to read binary data from a buffer
        def read_binary_data(gltf, bufferViewIndex):
            bufferView = gltf.bufferViews[bufferViewIndex]
            buffer = gltf.buffers[bufferView.buffer]

            # If the buffer contains a URI, it's an external file
            if buffer.uri:
                with open(os.path.join(directory, buffer.uri), 'rb') as f:
                    f.seek(bufferView.byteOffset)
                    return f.read(bufferView.byteLength)
            # Otherwise, the buffer is embedded in the GLTF file
            else:
                return buffer.data[bufferView.byteOffset:bufferView.byteOffset + bufferView.byteLength]

        # Load the GLTF file
        gltf = GLTF2().load(fpath)

        # Access the animations
        for animation in gltf.animations:
            print(f"Animation: {animation.name}")
            for channel in animation.channels:
                sampler = animation.samplers[channel.sampler]
                input_accessor = gltf.accessors[sampler.input]
                output_accessor = gltf.accessors[sampler.output]

                # Load keyframe data
                input_binary_data = read_binary_data(gltf, input_accessor.bufferView)
                output_binary_data = read_binary_data(gltf, output_accessor.bufferView)

                input_data = np.frombuffer(input_binary_data,
                                           dtype=COMPONENT_TYPE_TO_NUMPY[input_accessor.componentType])
                output_data = np.frombuffer(output_binary_data,
                                            dtype=COMPONENT_TYPE_TO_NUMPY[output_accessor.componentType])

            print(f"Keyframe Times: {input_data}")
            print(f"Keyframe Values: {output_data}")

        new_resource = Resource(resource_type=constants.RESOURCE_TYPE_MESH)

        gltf_header, gltf_data, gltf_dependencies = utils_gltf.load_gltf_parts(gltf_fpath=fpath)
        accessor_arrays = utils_gltf.extract_accessor_arrays(header=gltf_header, data=gltf_data)

        # Create meshes
        meshes = utils_gltf.load_meshes(header=gltf_header, accessor_arrays=accessor_arrays)
        for mesh_index, mesh in enumerate(meshes):

            # TODO: UVs are not yet implemented
            mesh_uid = f"{resource_uid}/mesh_{mesh_index}"
            self.create_mesh_resource(resource_uid=mesh_uid,
                                      vertices=mesh["positions"],
                                      normals=mesh["normals"],
                                      faces=mesh["indices"],
                                      uvs=None)

        # Create Nodes
        nodes = utils_gltf.load_nodes(header=gltf_header, accessor_arrays=accessor_arrays)

        # Create animations

        g = 0
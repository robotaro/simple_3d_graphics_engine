import os
import logging
import numpy as np

# Specifuc libraries for certain extensions
import trimesh

from src.core import constants
from src.core.data_block import DataBlock

from src.utilities import utils_obj, utils_bvh_reader


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

    def load_obj(self, resource_uid: str, fpath: str) -> None:

        mesh = trimesh.load(fpath)

        new_resource = Resource(resource_type=constants.RESOURCE_TYPE_MESH)

        new_resource.data_blocks["vertices"] = DataBlock(
            data_shape=mesh.vertices.shape,
            data_type=np.float32,
            data_format=constants.DATA_BLOCK_FORMAT_VEC3)
        new_resource.data_blocks["vertices"].data[:] = mesh.vertices

        new_resource.data_blocks["normals"] = DataBlock(
            data_shape=mesh.vertex_normals.shape,
            data_type=mesh.vertex_normals.dtype,
            data_format=constants.DATA_BLOCK_FORMAT_VEC3)
        new_resource.data_blocks["normals"].data[:] = mesh.vertices

        new_resource.data_blocks["faces"] = DataBlock(
            data_shape=mesh.faces.shape,
            data_type=np.int32,
            data_format=constants.DATA_BLOCK_FORMAT_VEC3)
        new_resource.data_blocks["faces"].data[:] = mesh.faces

        if "uv" in mesh.visual.__dict__:
            new_resource.data_blocks["uv"] = DataBlock(
                data_shape=mesh.visual.uv.shape,
                data_type=np.float32,
                data_format=constants.DATA_BLOCK_FORMAT_VEC2)
            new_resource.data_blocks["uv"].data[:] = mesh.visual.uv

        self.resources[resource_uid] = new_resource

    def load_bvh(self, resource_uid: str, fpath: str) -> Resource:

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
        vectorized_conversion = np.vectorize(constants.RESOURCE_BVH_ROT_ORDER_MAP.get)
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

        # Sort all postion-related animation data according to the order of the bones in the skeleton
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

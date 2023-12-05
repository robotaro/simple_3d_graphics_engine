import os
import logging
from typing import Union
import numpy as np

# Specifuc libraries for certain extensions
import trimesh

from src.core import constants
from src.core.data_block import DataBlock

from src.utilities import utils_obj, utils_bvh_reader, utils_gltf, utils_gltf_reader


class Resource:

    __slots__ = [
        "resource_type",
        "data_blocks",
        "metadata"
    ]

    def __init__(self, resource_type: str, metadata=None):
        self.resource_type = resource_type
        self.data_blocks = {}
        self.metadata = {} if metadata is None else metadata


class ResourceManager:

    __slots__ = [
        "logger",
        "resources",
        "extension_handlers"]

    def __init__(self, logger: logging.Logger):

        self.logger = logger
        self.resources = {}
        self.extension_handlers = {
            "obj": self.load_obj,
            "bvh": self.load_bvh,
            "gltf": self.load_gltf
        }

    def load_resource(self, resource_uid: str, fpath: str):

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
        new_resource.data_blocks["vertices"] = DataBlock(data=mesh.vertices)
        new_resource.data_blocks["normals"] = DataBlock(data=mesh.vertex_normals)
        new_resource.data_blocks["faces"] = DataBlock(data=mesh.faces)

        if "uv" in mesh.visual.__dict__:
            new_resource.data_blocks["uv"] = DataBlock(data=mesh.visual.uv)

        self.resources[resource_uid] = new_resource

    def load_bvh(self, resource_uid: str, fpath: str):

        bvh_reader = utils_bvh_reader.BVHReader()
        skeleton_df, animation_df, frame_period = bvh_reader.load(fpath=fpath)
        num_bones = skeleton_df.index.size
        bone_names = skeleton_df["name"].tolist()
        animation_columns = animation_df.columns.tolist()

        new_resource = Resource(resource_type=constants.RESOURCE_TYPE_MESH)

        # =========================[ Skeleton ]=========================

        new_resource.data_blocks["parent_index"] = DataBlock(data=skeleton_df["parent"].values, metadata=bone_names)

        pos_offset = skeleton_df[["position_x", "position_y", "position_z"]].values
        new_resource.data_blocks["position_offset"] = DataBlock(data=pos_offset)

        rot_offset = skeleton_df[["angle_offset_x", "angle_offset_y", "angle_offset_z"]].values
        new_resource.data_blocks["rotation_offset"] = DataBlock(data=rot_offset)

        new_resource.data_blocks["length"] = DataBlock(data=skeleton_df["length"].values)

        vectorized_conversion = np.vectorize(constants.RESOURCE_BVH_ROTATION_ORDER_MAP.get)
        rotation_order_integers = vectorized_conversion(skeleton_df["rotation_order"].values)
        new_resource.data_blocks["rotation_order"] = DataBlock(data=rotation_order_integers)

        # =========================[ Animation ]=========================
        num_frames = animation_df.index.size

        # Position Animation (if any)
        metadata = {"frame_period": frame_period}
        new_shape = (num_frames, num_bones, 3)
        new_position_datablock = DataBlock(data=np.zeros(new_shape, dtype=np.float32), metadata=metadata)
        new_rotation_datablock = DataBlock(data=np.zeros(new_shape, dtype=np.float32), metadata=metadata)

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

        gltf_reader = utils_gltf_reader.GLTFreader()
        gltf_reader.load(gltf_fpath=fpath)

        g = 0
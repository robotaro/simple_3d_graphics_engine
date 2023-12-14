import numpy as np
from src.utilities import utils_bvh_reader

from src.core import constants
from src.core.data_block import DataBlock
from src.core.data_group import DataGroup
from src.core.file_loaders.file_loader import FileLoader


class FileLoaderBVH(FileLoader):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def load(self, resource_uid: str, fpath: str) -> bool:

        bvh_reader = utils_bvh_reader.BVHReader()
        skeleton_df, animation_df, frame_period = bvh_reader.load(fpath=fpath)
        num_bones = skeleton_df.index.size
        bone_names = skeleton_df["name"].tolist()
        animation_columns = animation_df.columns.tolist()

        # =========================[ Skeleton ]=========================

        skeleton_resource = DataGroup(archetype=constants.RESOURCE_TYPE_SKELETON)

        skeleton_resource.data_blocks["parent_index"] = DataBlock(data=skeleton_df["parent"].values.astype(np.int32),
                                                                  metadata={"bone_names": bone_names})

        pos_offset = skeleton_df[["position_x", "position_y", "position_z"]].values
        skeleton_resource.data_blocks["position_offset"] = DataBlock(data=pos_offset)

        rot_offset = skeleton_df[["angle_offset_x", "angle_offset_y", "angle_offset_z"]].values.astype(np.float32)
        skeleton_resource.data_blocks["rotation_offset"] = DataBlock(data=rot_offset)

        skeleton_resource.data_blocks["length"] = DataBlock(data=skeleton_df["length"].values)

        vectorized_conversion = np.vectorize(constants.RESOURCE_BVH_ROTATION_ORDER_MAP.get)
        rotation_order_integers = vectorized_conversion(skeleton_df["rotation_order"].values)
        skeleton_resource.data_blocks["rotation_order"] = DataBlock(data=rotation_order_integers)

        complete_id = f"{resource_uid}/skeleton_0"

        self.external_data_groups[complete_id] = skeleton_resource

        # =========================[ Animation ]=========================

        animation_resource = DataGroup(archetype=constants.RESOURCE_TYPE_ANIMATION_BVH)

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

        animation_resource.data_blocks["animation_position"] = new_position_datablock
        animation_resource.data_blocks["animation_rotation"] = new_rotation_datablock

        self.external_data_groups[f"{resource_uid}/animation_0"] = animation_resource
        return True

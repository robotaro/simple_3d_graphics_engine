import re
import pandas as pd
import numpy as np

from skeleton.skeleton_blueprint import *

JOINTS_DF_KEY_LABEL = 'label'
JOINTS_DF_KEY_PARENT_INDEX = 'parent_index'
JOINTS_DF_KEY_OFFSET_X = 'offset_x'
JOINTS_DF_KEY_OFFSET_Y = 'offset_y'
JOINTS_DF_KEY_OFFSET_Z = 'offset_z'
JOINTS_DF_KEY_ROTATION_ORDER = 'rot_order'
END_SITE_KEY = 'end_site'
END_SITE_PLACEHOLDER_ROTATION_ORDER = 'none'


class BVHReader:

    def __init__(self):

        self.channel_map = {
            'Xposition': 'pos_x',
            'Yposition': 'pos_y',
            'Zposition': 'pos_z',
            'Xrotation': 'rot_x',
            'Yrotation': 'rot_y',
            'Zrotation': 'rot_z'
        }

        self.rotation_map = {
            'Xposition': '',
            'Yposition': '',
            'Zposition': '',
            'Xrotation': 'x',
            'Yrotation': 'y',
            'Zrotation': 'z'
        }

        # Original data from the .bvh
        self.num_frames = 0

    def load(self, fpath: str, scale=1.0):

        """
        Loads the skeleton and animation dataframe
        :param fpath:
        :param scale: float, value by which to multiply all joint offsets
        :return:
        """

        # Dataframe setup
        columns = [JOINTS_DF_KEY_LABEL,
                   JOINTS_DF_KEY_PARENT_INDEX,
                   JOINTS_DF_KEY_OFFSET_X,
                   JOINTS_DF_KEY_OFFSET_Y,
                   JOINTS_DF_KEY_OFFSET_Z,
                   JOINTS_DF_KEY_ROTATION_ORDER]
        joints_df = pd.DataFrame(columns=columns)

        # Temporary storage
        parents_index_list = []
        joint_name_list = []
        offset_list = []
        rot_order_list = []

        # Initializers
        current_index = -1
        end_site = False
        animation_columns = []
        animation_data = None
        frame_time = 0.0
        frame_index = 0

        file = open(fpath, "r")
        if file is None:
            raise Exception(f'[ERROR] Could not open file {fpath}')

        for line in file:

            # Skip non-important lines
            if any(key in line for key in ['HIERARCHY', 'MOTION', '{']):
                continue

            # ============== Skeleton ================
            if any(key in line for key in ['ROOT', 'JOINT']):
                joint_name_list.append(line.split()[1])
                parents_index_list.append(current_index)
                current_index = len(parents_index_list) - 1
                continue

            match_offset = re.match(r"\s*OFFSET\s+([\-\d\.e]+)\s+([\-\d\.e]+)\s+([\-\d\.e]+)", line)
            if match_offset:
                offset_list.append(list(map(np.float32, match_offset.groups())))
                if end_site:
                    rot_order_list.append(END_SITE_PLACEHOLDER_ROTATION_ORDER)
                continue

            match_channels = re.match(r"\s*CHANNELS\s+(\d+)", line)
            if match_channels:
                channels_list = line.split()[2:]
                animation_columns.extend([f'{joint_name_list[-1]}_{channel_map[key]}' for key in channels_list])
                rotation_order = ''.join([rotation_map[key] for key in channels_list])
                rot_order_list.append(rotation_order)
                continue

            if "End Site" in line:
                joint_name_list.append(END_SITE_KEY)
                parents_index_list.append(current_index)
                end_site = True
                continue

            if "}" in line:
                if end_site:
                    end_site = False
                else:
                    current_index = parents_index_list[current_index]
                continue

            # =============== Frames and Frame time ================

            match_frames = re.match("\s*Frames:\s+(\d+)", line)
            if match_frames:
                num_frames = int(match_frames.group(1))
                animation_data = np.ndarray((num_frames, len(animation_columns)), dtype=np.float32)
                continue

            match_frame_time = re.match("\s*Frame Time:\s+([\d\.]+)", line)
            if match_frame_time:
                frame_time = np.float32(match_frame_time.group(1))
                continue

            # If you got here, it means you finished with the skeleton
            joints_df[JOINTS_DF_KEY_LABEL] = joint_name_list
            joints_df[JOINTS_DF_KEY_PARENT_INDEX] = parents_index_list
            offsets = np.array(offset_list).astype(np.float32)
            joints_df[JOINTS_DF_KEY_OFFSET_X] = offsets[:, 0] * scale
            joints_df[JOINTS_DF_KEY_OFFSET_Y] = offsets[:, 1] * scale
            joints_df[JOINTS_DF_KEY_OFFSET_Z] = offsets[:, 2] * scale
            joints_df[JOINTS_DF_KEY_ROTATION_ORDER] = rot_order_list

            # =============== Motion ================

            # If you got here, it means this is the motion data part of the file
            # ALL OF THE ANGLES ARE STORED IN RADIANS! I HAVE SPOKEN!!!
            dmatch = line.strip().split()
            if dmatch:
                values = np.array(list(map(np.float32, dmatch)))
                # TODO: Re-do this properly so it is position agnostic

                animation_data[frame_index, :3] = values[:3]  # Root position
                animation_data[frame_index, 3:] = (values[3:] * np.pi) / 180.0  # Rotation
                frame_index += 1

        animation_df = pd.DataFrame(columns=animation_columns, data=animation_data)

        # Build a immediate child dependency list for using during bone length calculation
        generator = SkeletonBlueprintGenerator()
        children_lists = [[] for i in range(joints_df.index.size)]
        for index, joint in joints_df.iterrows():
            parent_index = joint[JOINTS_DF_KEY_PARENT_INDEX]
            if parent_index > -1:
                children_lists[parent_index].append(index)

        # Calculate bone lengths and add bone to blueprint
        for index, joint in joints_df.iterrows():

            # Bone length
            bone_length = 0
            if len(children_lists[index]) > 0:
                mean_children_pos = np.array([0, 0, 0], dtype=np.float32)
                for child_index in children_lists[index]:
                    mean_children_pos += joints_df.loc[child_index, JOINTS_DF_KEY_OFFSET_X:JOINTS_DF_KEY_OFFSET_Z].values.astype(np.float32)
                mean_children_pos /= len(children_lists[index])

                bone_pos = joints_df.loc[index, JOINTS_DF_KEY_OFFSET_X:JOINTS_DF_KEY_OFFSET_Z].values.astype(np.float32)
                bone_length = np.linalg.norm(mean_children_pos - bone_pos)

            # If this is the leaf bone, don't add it to the skeleton
            bone_name = joint[JOINTS_DF_KEY_LABEL]
            if bone_name == END_SITE_KEY:
                continue

            parent_index = joint[JOINTS_DF_KEY_PARENT_INDEX]
            parent_name = joints_df.at[parent_index, JOINTS_DF_KEY_LABEL] if parent_index > -1 else ''

            # Add new bone
            generator.add_bone(name=bone_name,
                               parent=parent_name,
                               pos_x=joint[JOINTS_DF_KEY_OFFSET_X],
                               pos_y=joint[JOINTS_DF_KEY_OFFSET_Y],
                               pos_z=joint[JOINTS_DF_KEY_OFFSET_Z],
                               length=bone_length,
                               rot_order=joint[JOINTS_DF_KEY_ROTATION_ORDER])

        blueprint_df = generator.create_blueprint()

        return blueprint_df, animation_df, frame_time


import numpy as np
import pandas as pd

PARAMS_NAME = "name"
PARAMS_PARENT = 'parent'
PARAMS_POS_X = "position_x"
PARAMS_POS_Y = "position_y"
PARAMS_POS_Z = "position_z"
PARAMS_ANGLE_OFFSET_X = "angle_offset_x"
PARAMS_ANGLE_OFFSET_Y = "angle_offset_y"
PARAMS_ANGLE_OFFSET_Z = "angle_offset_z"
PARAMS_ANGLE_MIN_X = "angle_min_x"
PARAMS_ANGLE_MIN_Y = "angle_min_y"
PARAMS_ANGLE_MIN_Z = "angle_min_z"
PARAMS_ANGLE_MAX_X = "angle_max_x"
PARAMS_ANGLE_MAX_Y = "angle_max_y"
PARAMS_ANGLE_MAX_Z = "angle_max_z"
PARAMS_LENGTH = "length"  # Length on the Y direction to help with visualisation
PARAMS_ROTATION_ORDER = "rotation_order"
PARAMS_DEFAULT_ROTATION = 'xyz'
PARAMS_COLUMNS = [PARAMS_NAME,
                  PARAMS_PARENT,
                  PARAMS_POS_X,
                  PARAMS_POS_Y,
                  PARAMS_POS_Z,
                  PARAMS_ANGLE_OFFSET_X,
                  PARAMS_ANGLE_OFFSET_Y,
                  PARAMS_ANGLE_OFFSET_Z,
                  PARAMS_ANGLE_MIN_X,
                  PARAMS_ANGLE_MIN_Y,
                  PARAMS_ANGLE_MIN_Z,
                  PARAMS_ANGLE_MAX_X,
                  PARAMS_ANGLE_MAX_Y,
                  PARAMS_ANGLE_MAX_Z,
                  PARAMS_LENGTH,
                  PARAMS_ROTATION_ORDER]

class SkeletonBlueprintGenerator:

    """
    The Skeleton Blueprint is a list of dictionaries that describe how

    """

    def __init__(self):
        self.bones = dict()

    def add_bone(self, name: str, parent='',
                 pos_x=0.0, pos_y=0.0, pos_z=0.0,
                 min_rot_x=0.0, min_rot_y=0.0, min_rot_z=0.0,
                 max_rot_x=0.0, max_rot_y=0.0, max_rot_z=0.0,
                 rot_offset_x=0.0, rot_offset_y=0.0, rot_offset_z=0.0,
                 length=0.0, rot_order=PARAMS_DEFAULT_ROTATION):

        # WARNING: Only one node must have the parent name empty ('') to denote the root node

        self.bones[name] = {PARAMS_NAME: name,
                            PARAMS_PARENT: parent,
                            PARAMS_POS_X: pos_x,
                            PARAMS_POS_Y: pos_y,
                            PARAMS_POS_Z: pos_z,
                            PARAMS_ANGLE_MIN_X: min_rot_x,
                            PARAMS_ANGLE_MIN_Y: min_rot_y,
                            PARAMS_ANGLE_MIN_Z: min_rot_z,
                            PARAMS_ANGLE_MAX_X: max_rot_x,
                            PARAMS_ANGLE_MAX_Y: max_rot_y,
                            PARAMS_ANGLE_MAX_Z: max_rot_z,
                            PARAMS_ANGLE_OFFSET_X: rot_offset_x,
                            PARAMS_ANGLE_OFFSET_Y: rot_offset_y,
                            PARAMS_ANGLE_OFFSET_Z: rot_offset_z,
                            PARAMS_LENGTH: length,
                            PARAMS_ROTATION_ORDER: rot_order}

    def create_blueprint(self) -> pd.DataFrame:

        # Step 1 ) Process root bone
        root_bone_names = []
        for key in self.bones.keys():
            if self.bones[key][PARAMS_PARENT] == '':
                root_bone_names.append(key)
        if len(root_bone_names) == 0:
            raise Exception('[ERROR] There is no root bone')
        if len(root_bone_names) > 1:
            raise Exception('[ERROR] There are more than one root bones')

        # Step 2 ) Process all remaining bones
        num_bones = len(self.bones.keys())
        bone_names_to_check = [root_bone_names[0]]  # Add the root bone to start with
        bone_counter = -1
        processed_bones = []
        while len(bone_names_to_check) > 0:

            if bone_counter > num_bones:
                raise Exception('[ERROR] There seems to be a loop in the bone hierarchy O_O')

            # Remove current bone from list to be checked
            current_bone_name = bone_names_to_check[0]
            bone_names_to_check.remove(current_bone_name)

            # And add to processed list
            current_bone = self.bones[current_bone_name]
            processed_bones.append(current_bone)

            # Now update its parent index
            parent_found = False
            for index, bone in enumerate(processed_bones):
                if bone[PARAMS_NAME] == current_bone[PARAMS_PARENT]:
                    current_bone[PARAMS_PARENT] = index
                    parent_found = True
            if not parent_found:
                current_bone[PARAMS_PARENT] = -1

            # Get all bones whose parent matches this bone name
            for name in self.bones.keys():
                if self.bones[name][PARAMS_PARENT] == current_bone_name:
                    bone_names_to_check.append(name)

            bone_counter += 1

        # Step 3) Convert list of dictionary into its final blueprint form
        bones_df = pd.DataFrame(processed_bones)

        return bones_df

    def save_blueprint(self):
        pass
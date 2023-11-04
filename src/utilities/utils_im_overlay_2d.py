import numpy as np
from numba import boolean, int32, float32
from numba.typed import List
from numba.experimental import jitclass

from src.core import constants

# Limits


# Command IDs
COMMAND_ID_AABB = 0.0
COMMAND_ID_CHARACTER = 1.0

# Command Array Column Indices
COL_INDEX_ID = 0
COL_INDEX_X = 1
COL_INDEX_Y = 2
COL_INDEX_WIDTH = 3
COL_INDEX_HEIGHT = 4
COL_INDEX_FILL_COLOR_RED = 5
COL_INDEX_FILL_COLOR_GREEN = 6
COL_INDEX_FILL_COLOR_BLUE = 7
COL_INDEX_FILL_COLOR_ALPHA = 8
COL_INDEX_EDGE_COLOR_RED = 9
COL_INDEX_EDGE_COLOR_GREEN = 10
COL_INDEX_EDGE_COLOR_BLUE = 11
COL_INDEX_EDGE_COLOR_ALPHA = 12

# Numba's class data type specification - required for internal optimisation
spec = [
    ('num_draw_commands', int32),
    ('draw_commands', float32[:, :]),
    ('max_draw_commands_limit_reached', boolean)
]

@jitclass(spec=spec)
class ImOverlay2D:

    """
    [ Immediate-Mode (IM) Overlay 2D Class ]
    You can use this class to efficiently create all 2D drawing instructions that will go with the
    overlay_2d.glsl program
    """

    def __init__(self):
        self.num_draw_commands = 0
        array_size = (constants.OVERLAY_2D_MAX_DRAW_COMMANDS, constants.OVERLAY_2D_NUM_COMMAND_COLUMNS)
        self.draw_commands = np.empty(array_size, dtype=np.float32)
        self.max_draw_commands_limit_reached = False

    def add_text(self, text: str):
        pass

    def add_aabb(self, x: float32, y: float32, width: float32, height: float32, fill_color=(1.0, 1.0, 1.0, 1.0)):

        if self.num_draw_commands == constants.OVERLAY_2D_MAX_DRAW_COMMANDS:
            return

        index = self.num_draw_commands

        # Command ID
        self.draw_commands[index, COL_INDEX_ID] = COMMAND_ID_AABB

        # Position
        self.draw_commands[index, COL_INDEX_X] = x
        self.draw_commands[index, COL_INDEX_Y] = y

        # Size
        self.draw_commands[index, COL_INDEX_WIDTH] = width
        self.draw_commands[index, COL_INDEX_HEIGHT] = height

        # Fill Color
        self.draw_commands[index, COL_INDEX_FILL_COLOR_RED] = fill_color[0]
        self.draw_commands[index, COL_INDEX_FILL_COLOR_GREEN] = fill_color[1]
        self.draw_commands[index, COL_INDEX_FILL_COLOR_BLUE] = fill_color[2]
        self.draw_commands[index, COL_INDEX_FILL_COLOR_ALPHA] = fill_color[3]


        self.num_draw_commands += 1

    def clear(self):
        self.num_draw_commands = 0
        self.max_draw_commands_limit_reached = False



import numpy as np
from numba import boolean, int32, float32
from numba.typed import List
from numba.experimental import jitclass

from src.core import constants

# Limits


# Command IDs
COMMAND_ID_AABB_FILLED = 0.0
COMMAND_ID_AABB_EDGE = 1.0
COMMAND_ID_CHARACTER = 2.0

# Command Array Column Indices
COL_INDEX_ID = 0
COL_INDEX_X = 1
COL_INDEX_Y = 2
COL_INDEX_WIDTH = 3
COL_INDEX_HEIGHT = 4
COL_INDEX_COLOR_RED = 5
COL_INDEX_COLOR_GREEN = 6
COL_INDEX_COLOR_BLUE = 7
COL_INDEX_COLOR_ALPHA = 8
COL_INDEX_EDGE_WIDTH = 9


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

    def add_aabb_filled(self,
                        x: float32,
                        y: float32,
                        width: float32,
                        height: float32,
                        color=(1.0, 1.0, 1.0, 1.0)):

        # Check if you can still fit this ome more draw command before proceeding
        if self.num_draw_commands == constants.OVERLAY_2D_MAX_DRAW_COMMANDS:
            return

        index = self.num_draw_commands

        # Command ID
        self.draw_commands[index, COL_INDEX_ID] = COMMAND_ID_AABB_FILLED

        # Position
        self.draw_commands[index, COL_INDEX_X] = x
        self.draw_commands[index, COL_INDEX_Y] = y

        # Size
        self.draw_commands[index, COL_INDEX_WIDTH] = width
        self.draw_commands[index, COL_INDEX_HEIGHT] = height

        # Color
        self.draw_commands[index, COL_INDEX_COLOR_RED] = color[0]
        self.draw_commands[index, COL_INDEX_COLOR_GREEN] = color[1]
        self.draw_commands[index, COL_INDEX_COLOR_BLUE] = color[2]
        self.draw_commands[index, COL_INDEX_COLOR_ALPHA] = color[3]

        self.num_draw_commands += 1

    def add_aabb_edge(self,
                      x: float32,
                      y: float32,
                      width: float32,
                      height: float32,
                      edge_width=1.0,
                      color=(1.0, 1.0, 1.0, 1.0)):

        # Check if you can still fit this ome more draw command before proceeding
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

        # Edge Width
        self.draw_commands[index, COL_INDEX_EDGE_WIDTH] = edge_width

        # Color
        self.draw_commands[index, COL_INDEX_COLOR_RED] = color[0]
        self.draw_commands[index, COL_INDEX_COLOR_GREEN] = color[1]
        self.draw_commands[index, COL_INDEX_COLOR_BLUE] = color[2]
        self.draw_commands[index, COL_INDEX_COLOR_ALPHA] = color[3]

        self.num_draw_commands += 1

    def clear(self):
        self.num_draw_commands = 0
        self.max_draw_commands_limit_reached = False



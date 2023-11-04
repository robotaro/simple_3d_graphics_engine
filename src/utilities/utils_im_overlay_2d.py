import numpy as np
from numba import boolean, int32, float32, uint8, bool_
from numba.typed import List
from numba.experimental import jitclass

from src.core import constants

# Limits


# Command IDs
COMMAND_ID_AABB = 0.0
COMMAND_ID_CHARACTER = 1.0

# Indices
COL_INDEX_ID = 0
COL_INDEX_X = 1
COL_INDEX_Y = 2
COL_INDEX_WIDTH = 3
COL_INDEX_HEIGHT = 4

spec = [
    ('num_draw_commands', int32),
    ('draw_commands', float32[:, :]),
    ('max_draw_commands_limit_reached', bool_)
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
        self.draw_commands = np.empty((constants.OVERLAY_2D_MAX_DRAW_COMMANDS, 9), dtype=np.float32)
        self.max_draw_commands_limit_reached = False

    def add_text(self, text: str):
        pass

    def add_aabb(self, x: float32, y: float32, width: float32, height: float32):

        if self.num_draw_commands == constants.OVERLAY_2D_MAX_DRAW_COMMANDS:
            return

        index = self.num_draw_commands
        self.draw_commands[index, COL_INDEX_ID] = COMMAND_ID_AABB
        self.draw_commands[index, COL_INDEX_X] = x
        self.draw_commands[index, COL_INDEX_Y] = y
        self.draw_commands[index, COL_INDEX_WIDTH] = width
        self.draw_commands[index, COL_INDEX_HEIGHT] = height
        self.num_draw_commands += 1

    def clear(self):
        self.num_draw_commands = 0
        self.max_draw_commands_limit_reached = False



import numpy as np
from numba import boolean, int32, float32, uint8
from numba.typed import List
from numba.experimental import jitclass


# Constants
MAX_NUM_DRAW_COMMANDS = 2048
COL_INDEX_X = 0
COL_INDEX_Y = 1
COL_INDEX_WIDTH = 2
COL_INDEX_HEIGHT = 3

spec = [
    ('num_draw_commands', int32),
    ('draw_commands', float32[:, :])
]


@jitclass(spec=spec)
class ImOverlay2D:

    def __init__(self):
        self.num_draw_commands = 0
        self.draw_commands = np.empty((MAX_NUM_DRAW_COMMANDS, 8), dtype=np.float32)

    def draw_text(self, text: str):
        pass

    def draw_aabb(self, x: float32, y: float32, width: float32, height: float32):

        pass


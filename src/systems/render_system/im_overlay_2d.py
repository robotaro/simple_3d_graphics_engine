import numpy as np
from numba import boolean, int32, float32
from numba.typed import List
from numba.experimental import jitclass

from src.core import constants

# Limits


# Command IDs
COMMAND_ID_AABB_FILLED = 0.0
COMMAND_ID_AABB_EDGE = 1.0
COMMAND_ID_AABB_TEXTURED = 2.0
COMMAND_ID_CIRCLE_FILL = 3.0
COMMAND_ID_CIRCLE_EDGE = 4.0
COMMAND_ID_CHARACTER = 5.0
COMMAND_ID_LINE_SEGMENT = 6.0

# Command Array Column Indices
COL_INDEX_COMMAND_ID = 0
COL_INDEX_X = 1
COL_INDEX_Y = 2
COL_INDEX_WIDTH = 3
COL_INDEX_HEIGHT = 4

COL_INDEX_POINT_A_X = 1
COL_INDEX_POINT_A_Y = 2
COL_INDEX_POINT_B_X = 3
COL_INDEX_POINT_B_Y = 4

COL_INDEX_RADIUS = 3  # Yep, same column for a different purpose on circles
COL_INDEX_COLOR_RED = 5
COL_INDEX_COLOR_GREEN = 6
COL_INDEX_COLOR_BLUE = 7
COL_INDEX_COLOR_ALPHA = 8
COL_INDEX_EDGE_WIDTH = 9
COL_INDEX_TEXTURE_INDEX = 9
COL_INDEX_U_MIN = 10
COL_INDEX_V_MIN = 11
COL_INDEX_U_MAX = 12
COL_INDEX_V_MAX = 13


# Special Characters
CHAR_SPACE = 32
CHAR_NEW_LINE = 10

# FOnt library copied-over constants
FONT_LIBRARY_COLUMN_INDEX_OFFSET_X = 0
FONT_LIBRARY_COLUMN_INDEX_OFFSET_Y = 1
FONT_LIBRARY_COLUMN_INDEX_WIDTH = 2
FONT_LIBRARY_COLUMN_INDEX_HEIGHT = 3
FONT_LIBRARY_COLUMN_INDEX_U_MIN = 4
FONT_LIBRARY_COLUMN_INDEX_V_MIN = 5
FONT_LIBRARY_COLUMN_INDEX_U_MAX = 6
FONT_LIBRARY_COLUMN_INDEX_V_MAX = 7

# Numba's class data type specification - required for internal optimisation
spec = [
    ('num_draw_commands', int32),
    ('draw_commands', float32[:, :]),
    ('character_data', float32[:, :]),
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
        self.character_data = np.empty((1, 1), dtype=np.float32)
        self.max_draw_commands_limit_reached = False

    def register_font(self, character_data: float32[:, :]):
        self.character_data = character_data

    def add_text(self, text: str, x: float32, y: float32):
        """
        Adds one character at time on the
        :param text:
        :return:
        """

        cursor_x = 0.0
        cursor_y = 0.0
        for _, char in enumerate(text):

            if self.num_draw_commands >= constants.OVERLAY_2D_MAX_DRAW_COMMANDS:
                continue

            index = self.num_draw_commands
            char_index = ord(char)

            if char_index == CHAR_SPACE:
                cursor_x += 10  # TODO: Think of better way to determine what space should be. Maybe use font itself

            # Command ID
            self.draw_commands[index, COL_INDEX_COMMAND_ID] = COMMAND_ID_CHARACTER

            # Position
            char_offset_x = self.character_data[char_index, FONT_LIBRARY_COLUMN_INDEX_OFFSET_X]
            char_offset_y = self.character_data[char_index, FONT_LIBRARY_COLUMN_INDEX_OFFSET_Y]
            self.draw_commands[index, COL_INDEX_X] = x + cursor_x
            self.draw_commands[index, COL_INDEX_Y] = y + cursor_y + char_offset_y

            # Size
            self.draw_commands[index, COL_INDEX_WIDTH] = self.character_data[char_index, FONT_LIBRARY_COLUMN_INDEX_WIDTH]
            self.draw_commands[index, COL_INDEX_HEIGHT] = self.character_data[char_index, FONT_LIBRARY_COLUMN_INDEX_HEIGHT]

            # UVs
            self.draw_commands[index, COL_INDEX_U_MIN] = self.character_data[char_index, FONT_LIBRARY_COLUMN_INDEX_U_MIN]
            self.draw_commands[index, COL_INDEX_V_MIN] = self.character_data[char_index, FONT_LIBRARY_COLUMN_INDEX_V_MIN]
            self.draw_commands[index, COL_INDEX_U_MAX] = self.character_data[char_index, FONT_LIBRARY_COLUMN_INDEX_U_MAX]
            self.draw_commands[index, COL_INDEX_V_MAX] = self.character_data[char_index, FONT_LIBRARY_COLUMN_INDEX_V_MAX]

            # Move curser forward for the next character
            cursor_x += self.character_data[char_index, constants.FONT_LIBRARY_COLUMN_INDEX_HORIZONTAL_ADVANCE]

            # Each character is draw command, so add it
            self.num_draw_commands += 1

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
        self.draw_commands[index, COL_INDEX_COMMAND_ID] = COMMAND_ID_AABB_FILLED

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
        self.draw_commands[index, COL_INDEX_COMMAND_ID] = COMMAND_ID_AABB_EDGE

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

        # Edge Width
        self.draw_commands[index, COL_INDEX_EDGE_WIDTH] = edge_width

        self.num_draw_commands += 1

    def add_aabb_textured(self,
                          x: float32,
                          y: float32,
                          width: float32,
                          height: float32,
                          texture_index: int32,
                          uv_min=(0.0, 0.0),
                          uv_max=(1.0, 1.0),
                          color=(1.0, 1.0, 1.0, 1.0)):

        # Check if you can still fit this ome more draw command before proceeding
        if self.num_draw_commands == constants.OVERLAY_2D_MAX_DRAW_COMMANDS:
            return

        index = self.num_draw_commands

        # Command ID
        self.draw_commands[index, COL_INDEX_COMMAND_ID] = COMMAND_ID_AABB_TEXTURED

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

    def add_circle_edge(self,
                        x: float32,
                        y: float32,
                        radius: float32,
                        edge_width=1.0,
                        color=(1.0, 1.0, 1.0, 1.0)):

        # Check if you can still fit this ome more draw command before proceeding
        if self.num_draw_commands == constants.OVERLAY_2D_MAX_DRAW_COMMANDS:
            return

        index = self.num_draw_commands

        # Command ID
        self.draw_commands[index, COL_INDEX_COMMAND_ID] = COMMAND_ID_CIRCLE_EDGE

        # Position
        self.draw_commands[index, COL_INDEX_X] = x
        self.draw_commands[index, COL_INDEX_Y] = y

        # Radius
        self.draw_commands[index, COL_INDEX_RADIUS] = radius

        # Color
        self.draw_commands[index, COL_INDEX_COLOR_RED] = color[0]
        self.draw_commands[index, COL_INDEX_COLOR_GREEN] = color[1]
        self.draw_commands[index, COL_INDEX_COLOR_BLUE] = color[2]
        self.draw_commands[index, COL_INDEX_COLOR_ALPHA] = color[3]

        # Edge Width
        self.draw_commands[index, COL_INDEX_EDGE_WIDTH] = edge_width

        self.num_draw_commands += 1

    def add_line_segments(self,
                          points_a: np.ndarray,
                          points_b: np.ndarray,
                          colors: np.ndarray,
                          edge=1.0):

        """
        This assumes both points_a, points_b and colors have the same length!
        """

        for point_index in range(points_a.shape[0]):

            # Check if you can still fit this ome more draw command before proceeding
            if self.num_draw_commands == constants.OVERLAY_2D_MAX_DRAW_COMMANDS:
                return

            cmd_index = self.num_draw_commands

            # Command ID
            self.draw_commands[cmd_index, COL_INDEX_COMMAND_ID] = COMMAND_ID_LINE_SEGMENT

            # Point A
            self.draw_commands[cmd_index, COL_INDEX_POINT_A_X] = points_a[point_index, 0]
            self.draw_commands[cmd_index, COL_INDEX_POINT_A_Y] = points_a[point_index, 1]

            # Point B
            self.draw_commands[cmd_index, COL_INDEX_POINT_B_X] = points_b[point_index, 0]
            self.draw_commands[cmd_index, COL_INDEX_POINT_B_Y] = points_b[point_index, 1]

            # Color
            self.draw_commands[cmd_index, COL_INDEX_COLOR_RED] = colors[point_index, 0]
            self.draw_commands[cmd_index, COL_INDEX_COLOR_GREEN] = colors[point_index, 1]
            self.draw_commands[cmd_index, COL_INDEX_COLOR_BLUE] = colors[point_index, 2]
            self.draw_commands[cmd_index, COL_INDEX_COLOR_ALPHA] = colors[point_index, 3]

            # Edge Width
            self.draw_commands[cmd_index, COL_INDEX_EDGE_WIDTH] = edge

            self.num_draw_commands += 1

    def clear(self):
        self.num_draw_commands = 0
        self.max_draw_commands_limit_reached = False



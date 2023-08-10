
# =============================================================================
#                               Event types
# =============================================================================

EVENT_KEYBOARD_PRESS = 1            # args: (key, scancode, mods) <int, int, int>
EVENT_KEYBOARD_RELEASE = 2          # args: (key, scancode, mods) <int, int, int>
EVENT_KEYBOARD_REPEAT = 3           # args: (key, scancode, mods) <int, int, int>

EVENT_MOUSE_BUTTON_PRESS = 4        # args: (button, mods) <int, int>
EVENT_MOUSE_BUTTON_RELEASE = 5      # args: (button, mods) <int, int>
EVENT_MOUSE_MOVE = 6                # args: (x, y) <float, float>
EVENT_MOUSE_SCROLL = 7              # args: (offset_x, offset_y) <float, float>

EVENT_WINDOW_RESIZE = 8                 # args: (width, height) <int, int>
EVENT_WINDOW_FRAMEBUFFER_RESIZE = 9     # args: (width, height) <int, int>
EVENT_WINDOW_DROP_FILES = 10             # args: (filepath, ...) <int, ...>  # TODO: Check if this should be a list


EVENT_LOAD_FILE = 1                 #args: (filepath) <str>
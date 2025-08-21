# application.py
"""Base application class - handles window, context, and input"""
import moderngl_window as mglw
from abc import ABC, abstractmethod


class Application(mglw.WindowConfig, ABC):
    """
    Base application class that provides:
    - Window management
    - OpenGL context
    - Input event handling
    - Main render loop
    """
    gl_version = (4, 3)
    title = "3D Application"
    window_size = (1600, 900)
    aspect_ratio = None
    vsync = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Mouse state tracking
        self.mouse_x = 0
        self.mouse_y = 0
        self.right_mouse_down = False
        self.left_mouse_down = False
        self.middle_mouse_down = False

        # Keyboard state
        self.keys_pressed = set()

        # Call child class initialization
        self.initialize()

    @abstractmethod
    def initialize(self):
        """Override this to initialize your application"""
        pass

    @abstractmethod
    def update(self, time: float, delta_time: float):
        """Override this to update and render your application"""
        pass

    def render(self, time: float, frametime: float):
        """Main render loop - calls update"""
        self.update(time, frametime)

    def resize(self, width: int, height: int):
        """Handle window resize"""
        self.window_size = (width, height)
        self.on_resize(width, height)

    def on_resize(self, width: int, height: int):
        """Override this to handle resize events"""
        pass

    # ========== Input Events ==========

    def key_event(self, key, action, modifiers):
        """Handle keyboard events"""
        if action == self.wnd.keys.ACTION_PRESS:
            self.keys_pressed.add(key)
            self.on_key_press(key, modifiers)
        elif action == self.wnd.keys.ACTION_RELEASE:
            self.keys_pressed.discard(key)
            self.on_key_release(key, modifiers)

    def mouse_position_event(self, x, y, dx, dy):
        """Handle mouse movement"""
        self.mouse_x = x
        self.mouse_y = y
        self.on_mouse_move(x, y, dx, dy)

    def mouse_press_event(self, x, y, button):
        """Handle mouse button press"""
        if button == 1:  # Left
            self.left_mouse_down = True
        elif button == 2:  # Right
            self.right_mouse_down = True
        elif button == 3:  # Middle
            self.middle_mouse_down = True

        self.on_mouse_press(x, y, button)

    def mouse_release_event(self, x, y, button):
        """Handle mouse button release"""
        if button == 1:  # Left
            self.left_mouse_down = False
        elif button == 2:  # Right
            self.right_mouse_down = False
        elif button == 3:  # Middle
            self.middle_mouse_down = False

        self.on_mouse_release(x, y, button)

    def mouse_drag_event(self, x, y, dx, dy):
        """Handle mouse drag"""
        self.on_mouse_drag(x, y, dx, dy)

    def mouse_scroll_event(self, x_offset, y_offset):
        """Handle mouse scroll"""
        self.on_mouse_scroll(x_offset, y_offset)

    # ========== Override these in your editor ==========

    def on_key_press(self, key: int, modifiers: int):
        """Override to handle key press"""
        pass

    def on_key_release(self, key: int, modifiers: int):
        """Override to handle key release"""
        pass

    def on_mouse_move(self, x: int, y: int, dx: int, dy: int):
        """Override to handle mouse movement"""
        pass

    def on_mouse_press(self, x: int, y: int, button: int):
        """Override to handle mouse button press"""
        pass

    def on_mouse_release(self, x: int, y: int, button: int):
        """Override to handle mouse button release"""
        pass

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int):
        """Override to handle mouse drag"""
        pass

    def on_mouse_scroll(self, x_offset: float, y_offset: float):
        """Override to handle mouse scroll"""
        pass

    # ========== Utility Methods ==========

    def is_key_pressed(self, key: int) -> bool:
        """Check if a key is currently pressed"""
        return key in self.keys_pressed
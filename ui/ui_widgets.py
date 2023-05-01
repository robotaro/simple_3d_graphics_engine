import numpy as np
import ui.ui_utils as utils

class UIWidget:

    _widget_type = 'undefined'

    def __init__(self,
                 widget_id: str,
                 width_str: str,
                 height_str: str,
                 level=0):

        # Initialize widget properties
        self._id = widget_id
        self.level = level
        self.width_pixels, self.width_ratio = utils.string2value(input_value=width_str)
        self.height_pixels, self.height_ratio = utils.string2value(input_value=height_str)
        self.x = 0.0
        self.y = 0.0

        # Topology
        self.parent = None
        self.children = []

    def add_child_widget(self, widget):
        # Add child widget to the list of widgets
        widget.parent = self
        self.children.append(widget)

    def draw_text(self, text: str, x: float, y: float):
        pass

    def draw(self, offset_x=0, offset_y=0) -> None:
        pass

    def update_dimensions(self):
        for child_widget in self.children:
            child_widget.update_dimensions()


# =======================================================================================
#                                   Window
# =======================================================================================


class UIWindow(UIWidget):

    _widget_type = 'window'

    def __init__(self, widget_id: str, width_str: str, height_str: str):
        super().__init__(widget_id=widget_id, width_str=width_str, height_str=height_str)
        self.title = ''

    def add_child_widget(self, widget):
        # TODO: Make UIWindow a UIWidget?
        widget.parent = self
        self.children.append(widget)


    def draw(self):
        # Render the GUI window and all widgets
        # Use ModernGL or other OpenGL techniques to render the window and widgets
        pass

# =======================================================================================
#                                      Column
# =======================================================================================

class UIColumn(UIWidget):

    _widget_type = 'column'

    def __init__(self, widget_id: str, width_str: str, height_str: str, spacing: float, level=0):
        # Initialize row properties
        super().__init__(widget_id=widget_id,
                         width_str=width_str,
                         height_str=height_str,
                         level=level)
        self.spacing = spacing

    def draw(self):
        # Render the row and all child widgets
        # Use ModernGL or other OpenGL techniques to render the row and its child widgets
        pass

    def update_dimensions(self):
        """
        :return:
        """

        # If width is fixed no further processing is required
        if self.width_ratio is None:
            for child_widget in self.children:
                child_widget.update_dimensions()
            return

        if self.parent is None:
            print('Impossible case?')
            parent_width = self.parent.width_pixels
            parent_height = self.parent.height_pixels

        # Update width
        num_children = len(self.children)
        self.width_pixels = self.width_ratio * self.parent.width_pixels
        total_width = self.width_pixels - (self.spacing * (num_children - 1))
        widget_width = total_width / num_children

        for child_widget in self.children:
            child_widget.update_dimensions()


# =======================================================================================
#                                      Row
# =======================================================================================

class UIRow(UIWidget):

    _widget_type = 'row'

    def __init__(self, widget_id: str, width_str: str, height_str: str, spacing: float, level=0):
        # Initialize row properties
        super().__init__(widget_id=widget_id,
                         width_str=width_str,
                         height_str=height_str,
                         level=level)
        self.spacing = spacing
        self.widgets = []  # List to store child widgets

    def set_width(self, width):
        # Set the width of the row and update the widths of child widgets
        self.width = width
        total_width = self.width - (self.spacing * (len(self.widgets) - 1))  # Total width available for widgets
        widget_width = total_width / len(self.widgets)  # Width per widget

        for widget in self.widgets:
            widget.set_width(widget_width)

    def draw(self):
        # Render the row and all child widgets
        # Use ModernGL or other OpenGL techniques to render the row and its child widgets
        pass

# =======================================================================================
#                                   Button
# =======================================================================================

class UIButton(UIWidget):

    _widget_type = 'button'

    def __init__(self, widget_id: str, width_str: str, height_str: str, text: str, level=0):
        # Initialize button properties
        super().__init__(widget_id=widget_id,
                         width_str=width_str,
                         height_str=height_str,
                         level=level)
        self.text = text

    def draw(self, offset_x=0, offset_y=0) -> None:
        # Render the button
        # Use ModernGL or other OpenGL techniques to render the button with its text

        # Draw button background

        # Draw button text

        pass

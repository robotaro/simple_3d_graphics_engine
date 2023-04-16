import numpy as np


class GUIWidget:

    def __init__(self, width, height):

        # Initialize widget properties
        self.width = width
        self.height = height
        self.parent = None  # Parent widget, initially set to None

    def set_width(self, width, parent_width=None):

        # Set the width of the widget
        if isinstance(width, str):
            # If width is a string, assume it's a percentage and calculate the width accordingly
            if parent_width is None:
                raise ValueError("Parent width is required for percentage-based width")
            percentage = float(width.rstrip('%')) / 100
            self.width = int(parent_width * percentage)
        else:
            # If width is an integer, use it as the fixed width
            self.width = width

    def set_height(self, height, parent_height=None):
        # Set the height of the widget
        if isinstance(height, str):
            # If height is a string, assume it's a percentage and calculate the height accordingly
            if parent_height is None:
                raise ValueError("Parent height is required for percentage-based height")
            percentage = float(height.rstrip('%')) / 100
            self.height = int(parent_height * percentage)
        else:
            # If height is an integer, use it as the fixed height
            self.height = height

    def draw_text(self, text: str, x: float, y: float):
        pass

    def draw(self, offset_x=0, offset_y=0) -> None:
        # Render the widget
        # Use ModernGL or other OpenGL techniques to render the widget
        pass

    def update_size(self):
        pass


class GUIRow(GUIWidget):
    def __init__(self, width, height, spacing):
        # Initialize row properties
        super().__init__(width, height)
        self.spacing = spacing
        self.widgets = []  # List to store child widgets

    def add_widget(self, widget):
        # Add child widget to the list of widgets
        self.widgets.append(widget)

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

    # Other methods for handling events, updating state, etc.


class GUIButton(GUIWidget):
    def __init__(self, width, height, text):
        # Initialize button properties
        super().__init__(width, height)
        self.text = text

    def draw(self, offset_x=0, offset_y=0) -> None:
        # Render the button
        # Use ModernGL or other OpenGL techniques to render the button with its text

        # Draw button background

        # Draw button text

        pass

    # Other methods for handling events, updating state, etc.

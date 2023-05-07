from ui.widgets.ui_widget import UIWidget

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
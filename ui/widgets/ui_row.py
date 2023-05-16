from ui.widgets.ui_widget import UIWidget


class UIRow(UIWidget):

    _widget_type = 'row'

    def __init__(self, widget_id: str, width_str: str, height_str: str, spacing: float, level=0):
        # Initialize row properties
        super().__init__(widget_id=widget_id,
                         width_str=width_str,
                         height_str=height_str,
                         spacing_x=spacing,
                         level=level)
        self.widgets = []  # List to store child widgets


    def draw(self):
        # Render the row and all child widgets
        # Use ModernGL or other OpenGL techniques to render the row and its child widgets

        # Generate vertices here

        pass
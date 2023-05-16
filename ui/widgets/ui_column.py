from ui.widgets.ui_widget import UIWidget

class UIColumn(UIWidget):

    _widget_type = 'column'

    def __init__(self, widget_id: str, width_str: str, height_str: str, spacing: float, level=0):
        # Initialize row properties
        super().__init__(widget_id=widget_id,
                         width_str=width_str,
                         height_str=height_str,
                         spacing_y=spacing,
                         level=level)
        self.spacing = spacing

    def draw(self):
        # Render the row and all child widgets
        # Use ModernGL or other OpenGL techniques to render the row and its child widgets
        pass

    def update_position(self):

        pass


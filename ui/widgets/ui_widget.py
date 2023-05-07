from ui import ui_utils

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
        self.width_pixels, self.width_ratio = ui_utils.string2value(input_value=width_str)
        self.height_pixels, self.height_ratio = ui_utils.string2value(input_value=height_str)
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

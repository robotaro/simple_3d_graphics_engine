from ui.widgets.ui_widget import UIWidget

class UIWindow(UIWidget):

    _widget_type = 'window'

    def __init__(self, widget_id: str, width_str: str, height_str: str):
        super().__init__(widget_id=widget_id, width_str=width_str, height_str=height_str)
        self.title = ''

    def add_child_widget(self, widget):
        widget.parent = self
        self.children.append(widget)

    def update_positions(self):
        pass

    def draw(self):
        # Render the GUI window and all widgets
        # Use ModernGL or other OpenGL techniques to render the window and widgets
        pass

from ui.widgets.ui_widget import UIWidget

class UIWindow(UIWidget):

    _widget_type = 'window'

    def __init__(self,
                 widget_id: str,
                 width_str: str,
                 height_str: str,
                 title='No Title',
                 x=0,
                 y=0):
        super().__init__(widget_id=widget_id, width_str=width_str, height_str=height_str)
        self.x = x
        self.y = y
        self.title = title

    def add_child_widget(self, widget):
        widget.parent = self
        self.children.append(widget)

    def update_positions(self):
        pass

    def draw(self):

        super().draw()

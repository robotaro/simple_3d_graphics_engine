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

    def update_child_positions(self) -> None:

        # NOTE: Window should only have ONE child!
        if len(self.children) > 1:
            print('[WARNING] Window widget should only have one child!')

        self.children[0].x = self.x + self.spacing_x
        self.children[0].y = self.y + self.spacing_y

from ui.widgets.ui_widget import UIWidget

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

        # WIDTH
        if self.width_ratio is None:
            for child_widget in self.children:
                child_widget.update_dimensions()
        else:
            self.width_pixels = self.width_ratio * self.parent.width_pixels
            # num_children = len(self.children)
            # total_width = self.width_pixels - (self.spacing * (num_children - 1))
            # self.width_pixels = total_width / num_children

        # HEIGHT
        if self.height_ratio is None:
            for child_widget in self.children:
                child_widget.update_dimensions()
        else:
            self.width_pixels = self.width_ratio * self.parent.width_pixels
            # num_children = len(self.children)
            # total_width = self.width_pixels - (self.spacing * (num_children - 1))
            # self.width_pixels = total_width / num_children

        for child_widget in self.children:
            child_widget.update_dimensions()

    def update_position(self):

        pass


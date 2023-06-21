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

    def update_child_positions(self) -> None:

        """
        TODO: This can only be called after all children have updated their dimensions
        :return: None
        """

        center_x = self.x + self.width_pixels * 0.5

        y_offset = self.y + self.spacing_y
        for child in self.children:
            child.x = center_x - child.width_pixels * 0.5
            child.y = y_offset
            y_offset += child.height_pixels + self.spacing_y
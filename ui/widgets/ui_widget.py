from ui import ui_utils
from ui import ui_constants as constants
import numpy as np


class UIWidget:

    _widget_type = 'base_widget'

    def __init__(self,
                 widget_id: str,
                 width_str: str,
                 height_str: str,
                 spacing_x=0,
                 spacing_y=0,
                 level=0):

        # Initialize widget properties
        self._id = widget_id
        self.level = level
        self.width_pixels, self.width_ratio = ui_utils.string2value(input_value=width_str)
        self.height_pixels, self.height_ratio = ui_utils.string2value(input_value=height_str)

        self.x = 0.0
        self.y = 0.0
        self.spacing_x = spacing_x
        self.spacing_y = spacing_y

        self.vertices = np.ndarray((constants.DEFAULT_WIDGET_MAX_NUM_VERTICES, 3), dtype=np.float32)
        self.num_vertices = 0

        # Topology
        self.parent = None
        self.children = []

    @property
    def num_children(self):
        return len(self.children)

    def add_child_widget(self, widget):
        # Add child widget to the list of widgets
        widget.parent = self
        self.children.append(widget)

    def draw_text(self, text: str, x: float, y: float):
        pass

    def draw(self) -> None:
        for child in self.children:
            child.draw()

    def get_children_fixed_width_sum(self) -> int:
        return sum([child.width_pixels for child in self.children if child.width_ratio is None])

    def get_children_fixed_height_sum(self) -> int:
        return sum([child.height_pixels for child in self.children if child.height_ratio is None])

    def update_dimensions(self):

        if self.width_ratio is not None:
            parent_spacing_sum = max(2, len(self.parent.children) + 1) * self.parent.spacing_x
            parent_children_width_sum = self.parent.get_children_fixed_width_sum()
            parent_available_width = self.parent.width_pixels - parent_spacing_sum - parent_children_width_sum
            self.width_pixels = self.width_ratio * parent_available_width

        if self.height_ratio is not None:
            parent_spacing_sum = max(2, len(self.parent.children) + 1) * self.parent.spacing_y
            parent_children_height_sum = self.parent.get_children_fixed_width_sum()
            parent_available_height = self.parent.height_pixels - parent_spacing_sum - parent_children_height_sum
            self.height_pixels = self.height_ratio * parent_available_height

        for child_widget in self.children:
            child_widget.update_dimensions()

    def update_position(self):
        """
        This should be called at the end of each overwritten update_position
        :return:
        """

        self.update_child_positions()

        for child_widget in self.children:
            child_widget.update_position()

    def update_child_positions(self) -> None:
        # Abstract
        pass

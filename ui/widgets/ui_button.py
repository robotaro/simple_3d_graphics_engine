from ui.widgets.ui_widget import UIWidget


class UIButton(UIWidget):

    _widget_type = 'button'

    def __init__(self, widget_id: str, width_str: str, height_str: str, text: str, level=0):

        # Initialize button properties
        super().__init__(widget_id=widget_id,
                         width_str=width_str,
                         height_str=height_str,
                         level=level)

        self.text = text

    def draw(self, offset_x=0, offset_y=0) -> None:
        # Render the button
        # Use ModernGL or other OpenGL techniques to render the button with its text

        # Draw button background


        # Draw button text


        pass


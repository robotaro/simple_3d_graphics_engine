import json
from bs4 import BeautifulSoup
import warnings
from bs4 import GuessedAtParserWarning
warnings.filterwarnings('ignore', category=GuessedAtParserWarning)

from ui.ui_font import UIFont
from ui.widgets.ui_widget import UIWidget
from ui.widgets.ui_window import UIWindow
from ui.widgets.ui_row import UIRow
from ui.widgets.ui_column import UIColumn
from ui.widgets.ui_button import UIButton

import ui.ui_constants as constants

class UICore:

    def __init__(self):

        self.windows = []
        self.font = UIFont()

    def load(self, blueprint_xml_fpath: str, theme_json_fpath: str) -> None:
        
        """
        Loads current UI described in the ui blueprint
        :param blueprint_xml_fpath:
        :param theme_json_fpath:
        :return: None
        """

        # Load UI theme
        with open(theme_json_fpath, 'r') as file:
            # Load theme
            self.theme = json.load(file)

            # Load font here
            self.font.load(ttf_fpath=self.theme['font']['filepath'])

        # Load UI window blueprint
        with open(blueprint_xml_fpath) as file:
            root_soup = BeautifulSoup(file.read(), features="lxml")

            # Find window root node - there should be only one
            ui_soup = root_soup.find("ui")
            if ui_soup is None:
                raise ValueError(f"[ERROR] Could not find UI root '<ui>'")

            for window_soup in root_soup.find_all("window"):
                window_widget = UIWindow(
                    widget_id=window_soup.attrs.get('id', 'no_id'),
                    width_str=window_soup.attrs.get('height', '100%'),
                    height_str=window_soup.attrs.get('height', '100%'))

                self.windows.append(window_widget)
                self.build_widget_tree(parent_soup=window_soup, parent_widget=window_widget)

    def build_widget_tree(self, parent_soup: BeautifulSoup, parent_widget: UIWidget, level=0):

        level += 1

        for child_soup in parent_soup.findChildren(recursive=False):
            attrs = child_soup.attrs
            new_widget = None

            if "id" not in attrs:
                raise AttributeError(f"[ERROR] Missing widget ID on {attrs.name} widget")

            if child_soup.name == "column":
                width_str = attrs.get('width', '100%')
                height_str = attrs.get('height', '100%')
                spacing = attrs.get('spacing', constants.DEFAULT_SPACING_ROW)
                new_widget = UIColumn(
                    widget_id=attrs["id"],
                    width_str=width_str,
                    height_str=height_str,
                    spacing=float(spacing),
                    level=level)
                parent_widget.add_child_widget(widget=new_widget)

            if child_soup.name == "row":
                width_str = attrs.get('width', '100%')
                height_str = attrs.get('height', '100%')
                spacing = attrs.get('spacing', constants.DEFAULT_SPACING_ROW)
                new_widget = UIRow(
                    widget_id=attrs["id"],
                    width_str=width_str,
                    height_str=height_str,
                    spacing=float(spacing),
                    level=level)
                parent_widget.add_child_widget(widget=new_widget)

            if child_soup.name == 'button':
                width_str = attrs.get('width', '100%')
                height_str = attrs.get('height', '100%')
                text = 'No text' if len(child_soup.text) == 0 else child_soup.text

                new_widget = UIButton(
                    widget_id=attrs["id"],
                    width_str=width_str,
                    height_str=height_str,
                    text=text,
                    level=level)
                parent_widget.add_child_widget(widget=new_widget)

            if new_widget is None:
                break

            self.build_widget_tree(parent_soup=child_soup, parent_widget=new_widget, level=level)

    def update_dimensions(self):
        for window in self.windows:
            window.update_dimensions()

    def update_position(self):
        for window in self.windows:
            window.update_positions()

    # =======================================================
    #                       DEBUG
    # =======================================================

    def print_widget_tree(self):
        """
        Prints current UI structure on the terminal for debuggin purposes

        :return:
        """

        def recursive_print(widget: UIWidget):
            spaces = ' ' * (widget.level * 2)
            print(f'{spaces}> {widget._widget_type} : {widget._id} ({widget.width_pixels}, {widget.height_pixels})')
            for child_widget in widget.children:
                recursive_print(child_widget)

        for window in self.windows:
            recursive_print(window)

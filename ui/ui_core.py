import json
from bs4 import BeautifulSoup
import warnings
from bs4 import GuessedAtParserWarning

from ui.ui_font import UIFont
from ui.widgets.ui_widget import UIWidget
from ui.widgets.ui_window import UIWindow
from ui.widgets.ui_row import UIRow
from ui.widgets.ui_column import UIColumn
from ui.widgets.ui_button import UIButton
from ui import ui_constants

# [ DEBUG ]
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

warnings.filterwarnings('ignore', category=GuessedAtParserWarning)


class UICore:

    def __init__(self):

        self.windows = []
        self.font = UIFont()

    def load(self, blueprint_xml_fpath: str, theme_json_fpath: str, font_ttf_fpath: str) -> None:

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

            # Load font
            self.font.load(ttf_fpath=font_ttf_fpath)

        # Load UI window blueprint
        with open(blueprint_xml_fpath) as file:
            root_soup = BeautifulSoup(file.read(), features="lxml")

            # Find window root node - there should be only one
            ui_soup = root_soup.find(ui_constants.KEY_ELEMENT_UI)
            if ui_soup is None:
                raise ValueError(f"[ERROR] Could not find UI root '<{ui_constants.KEY_ELEMENT_UI}>'")

            for window_soup in root_soup.find_all(ui_constants.KEY_ELEMENT_WINDOW):
                window_widget = UIWindow(
                    widget_id=window_soup.attrs.get(ui_constants.KEY_ATTRS_ID, 'no_id'),
                    width_str=window_soup.attrs.get(ui_constants.KEY_ATTRS_WIDTH, '100%'),
                    height_str=window_soup.attrs.get(ui_constants.KEY_ATTRS_HEIGHT, '100%'),
                    x=float(window_soup.attrs.get(ui_constants.KEY_ATTRS_X, '0')),
                    y=float(window_soup.attrs.get(ui_constants.KEY_ATTRS_Y, '0')),
                )

                self.windows.append(window_widget)
                self.build_widget_tree(parent_soup=window_soup, parent_widget=window_widget)

    def build_widget_tree(self, parent_soup: BeautifulSoup, parent_widget: UIWidget, level=0):

        level += 1

        for child_soup in parent_soup.findChildren(recursive=False):
            new_widget = None

            if ui_constants.KEY_ATTRS_ID not in child_soup.attrs:
                raise AttributeError(f"[ERROR] Missing widget ID on {child_soup.attrs.name} widget")

            if child_soup.name == ui_constants.KEY_ELEMENT_COLUMN:
                new_widget = self.soup2ui_column(soup=child_soup, level=level)
                parent_widget.add_child_widget(widget=new_widget)

            if child_soup.name == ui_constants.KEY_ELEMENT_ROW:
                new_widget = self.soup2ui_row(soup=child_soup, level=level)
                parent_widget.add_child_widget(widget=new_widget)

            if child_soup.name == ui_constants.KEY_ELEMENT_BUTTON:
                new_widget = self.soup2ui_button(soup=child_soup, level=level)
                parent_widget.add_child_widget(widget=new_widget)

            if new_widget is None:
                raise ValueError(f"[ERROR] Widget type {child_soup.name} is not supported")

            self.build_widget_tree(parent_soup=child_soup, parent_widget=new_widget, level=level)

    @staticmethod
    def soup2ui_column(soup: BeautifulSoup, level: int) -> UIColumn:
        width_str = soup.attrs.get(ui_constants.KEY_ATTRS_WIDTH, '100%')
        height_str = soup.attrs.get(ui_constants.KEY_ATTRS_HEIGHT, '100%')
        spacing = soup.attrs.get(ui_constants.KEY_ATTRS_SPACING, ui_constants.DEFAULT_SPACING_COLUMN)
        return UIColumn(
            widget_id=soup.attrs[ui_constants.KEY_ATTRS_ID],
            width_str=width_str,
            height_str=height_str,
            spacing=float(spacing),
            level=level)

    @staticmethod
    def soup2ui_row(soup: BeautifulSoup, level: int) -> UIRow:
        width_str = soup.attrs.get(ui_constants.KEY_ATTRS_WIDTH, '100%')
        height_str = soup.attrs.get(ui_constants.KEY_ATTRS_HEIGHT, '100%')
        spacing = soup.attrs.get(ui_constants.KEY_ATTRS_SPACING, ui_constants.DEFAULT_SPACING_ROW)
        return UIRow(
            widget_id=soup.attrs[ui_constants.KEY_ATTRS_ID],
            width_str=width_str,
            height_str=height_str,
            spacing=float(spacing),
            level=level)

    @staticmethod
    def soup2ui_button(soup: BeautifulSoup, level: int) -> UIButton:
        width_str = soup.attrs.get(ui_constants.KEY_ATTRS_WIDTH, '100%')
        height_str = soup.attrs.get(ui_constants.KEY_ATTRS_HEIGHT, '100%')
        text = 'No text' if len(soup.text) == 0 else soup.text
        return UIButton(
            widget_id=soup.attrs[ui_constants.KEY_ATTRS_ID],
            width_str=width_str,
            height_str=height_str,
            text=text,
            level=level)

    def update_dimensions(self):
        for window in self.windows:
            window.update_dimensions()

    def update_positions(self):
        for window in self.windows:
            window.update_positions()

    def draw(self):
        for window in self.windows:
            window.draw()

    # =======================================================
    #                       DEBUG
    # =======================================================

    def print_widget_tree(self):
        """
        Prints current UI structure on the terminal for debugging purposes

        :return:
        """

        def recursive_print(widget: UIWidget):
            spaces = ' ' * (widget.level * 2)
            dimensions = f"({widget.width_pixels}, {widget.height_pixels})"
            positions = f"({widget.x}, {widget.y})"
            print(f"{spaces}> {widget._widget_type} : {widget._id} {dimensions} {positions}")
            for child_widget in widget.children:
                recursive_print(child_widget)

        for window in self.windows:
            recursive_print(window)

    def show_debug_plot(self):

        def recursive_get_dimensions(widget: UIWidget, widget_dimensions: list):

            rectangle = (widget._widget_type,
                         widget.x,
                         widget.y,
                         widget.width_pixels,
                         widget.height_pixels)
            widget_dimensions.append(rectangle)

            for child_widget in widget.children:
                recursive_get_dimensions(widget=child_widget, widget_dimensions=widget_dimensions)

        fig, ax = plt.subplots(1)

        for window in self.windows:

            list_of_dimensions = []
            recursive_get_dimensions(widget=window, widget_dimensions=list_of_dimensions)

            rectangles = [Rectangle((item[1], item[2]), item[3], item[4], facecolor="none", edgecolor="b")
                          for item in list_of_dimensions]

            # Add collection to axes
            for rectangle in rectangles:
                ax.add_patch(rectangle)

        ax.set_xlim(0, 1600)
        ax.set_ylim(0, 1000)
        ax.invert_yaxis()
        ax.set_aspect("equal")
        plt.tight_layout()

        plt.show()


import os

from ui.ui_core import UICore
from ui.ui_font import UIFont


def fix_path(input_path: str):
    working_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(working_dir, input_path).replace("/", os.sep).replace("\\", os.sep)


def main():

    xml_fath = fix_path(input_path=os.path.join(*["data", "ui", "ui_blueprint.xml"]))
    json_fath = fix_path(input_path=os.path.join(*["data", "ui", "default_theme.json"]))
    font_fpath = fix_path(input_path=os.path.join(*["data", "fonts", "ProggyClean.ttf"]))

    ui = UICore()
    ui.load(blueprint_xml_fpath=xml_fath, theme_json_fpath=json_fath, font_ttf_fpath=font_fpath)
    ui.update_dimensions()
    ui.update_positions()
    ui.draw()
    ui.print_widget_tree()


if __name__ == "__main__":
    main()

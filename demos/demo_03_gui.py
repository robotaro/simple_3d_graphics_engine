from ui.ui_core import UICore
from ui.ui_font import UIFont

if __name__ == "__main__":
    from bs4 import BeautifulSoup

    #xml = '<root><element>data</element></root>'
    #soup = BeautifulSoup(xml, 'lxml')
    #root_tag = soup.find('root')
    #element_tag = root_tag.find('element', recursive=False)

    xml_fath = "data/ui/ui_blueprint.xml"
    font_fpath = "data/fonts/ProggyClean.ttf"
    json_fath = "data/ui/default_theme.json"

    font = UIFont()
    font.load(ttf_fpath=font_fpath)

    ui = UICore()
    ui.load(blueprint_xml_fpath=xml_fath, theme_json_fpath=json_fath)
    ui.update_dimensions()
    ui.print_widget_tree()

    #ui.update_positions()

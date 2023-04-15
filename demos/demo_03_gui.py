from ui.ui_window import UIWindow

if __name__ == "__main__":

    xml_fath = "data/ui/ui_blueprint.xml"
    json_fath = "data/ui/default_theme.json"

    ui_window = UIWindow()
    ui_window.load(window_id="window_01",
                   blueprint_xml_fpath=xml_fath,
                   theme_json_fpath=json_fath)

    g = 0
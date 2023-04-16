

class UIWindow:

    def __init__(self, width, height, title):
        # Initialize window properties
        self.width = width
        self.height = height
        self.title = title
        self.widgets = []  # List to store all widgets

    def load(self, blueprint_xml_fpath: str, window_id: str, theme_json_fpath: str):
        # Load UI theme
        with open(theme_json_fpath, 'r') as file:
            # Load theme
            self.theme = json.load(file)

            # Load font here
            self.font.load(ttf_fpath=self.theme['font']['filepath'])

        # Load UI window blueprint
        with open(blueprint_xml_fpath) as file:
            root_soup = BeautifulSoup(file.read(), features="html.parser")

            # Find window root node - there should be only one
            window_soup = root_soup.find("window", recursive=False)
            if window_soup is None:
                raise ValueError(f"[ERROR] Could not find blueprint for window {window_id}")

            widget_pre_node_list = ui_utils.generate_widget_preprocessed_node_list(window_soup=window_soup)
            widget_index_map = ui_utils.generate_widget_index_map(widget_pre_node_list=widget_pre_node_list,
                                                                  window_id=window_id)
            widgets = ui_utils.generate_widget_node_list(widget_pre_node_list=widget_pre_node_list,
                                                         widget_index_map=widget_index_map)
            self.initialize_widgets(widgets=widgets, theme=self.theme)
            self.update_widgets()

    def add_widget(self, widget):
        # Add widget to the list of widgets
        self.widgets.append(widget)

    def draw(self):
        # Render the GUI window and all widgets
        # Use ModernGL or other OpenGL techniques to render the window and widgets
        pass

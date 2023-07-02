import numpy as np
import json
from bs4 import BeautifulSoup
import freetype
from typing import List, Union, Tuple


import ui.ui_window_dod_utils as ui_utils
from ui.ui_font import UIFont
from ui import ui_constants as constants

class UIWindowDOD:
    
    NUM_WIDGET_CONNECTIONS = 4
    NUM_WIDGET_PROPERTIES = 15
    
    INDEX_PARENT = 0
    INDEX_NEXT = 1
    INDEX_PREV = 2
    INDEX_FIRST_CHILD = 3
    
    INDEX_X = 0
    INDEX_Y = 1
    INDEX_WIDTH = 2
    INDEX_HEIGHT = 3
    INDEX_TARGET_WIDTH = 4
    INDEX_TARGET_HEIGHT = 5
    INDEX_PAD_TOP = 6
    INDEX_PAD_LEFT = 7
    INDEX_PAD_BOTTOM = 8
    INDEX_PAD_RIGHT = 9
    INDEX_SPACING = 10
    INDEX_SUM_INTERNAL_FIXED_WIDTH = 11
    INDEX_SUM_INTERNAL_FIXED_HEIGHT = 12
    INDEX_SUM_INTERNAL_VARIABLE_WIDTH = 13
    INDEX_SUM_INTERNAL_VARIABLE_HEIGHT = 14
    
    # TODO: Add slots here to optmise data access
    def __init__(self) -> None:
        
        self.theme = None
        
        # UI Window Variables
        self.window_title = 'Untitled Window'
        self.window_x = 0
        self.window_y = 0
        self.window_width = 0
        self.window_height = 0
        self.window_title_height = 40
        self.window_padding_left = 5
        self.window_padding_top = 5
        self.window_padding_right = 5
        self.window_padding_bottom = 5
        
        # UI Widgets variables
        self.widget_types = np.ndarray((0, ), dtype=np.int32)
        self.widget_num_children = np.ndarray((0, ), dtype=np.int32)
        self.widget_connections = np.ndarray((0, UIWindow.NUM_WIDGET_CONNECTIONS), dtype=np.int32)
        self.widget_properties = np.ndarray((0, UIWindow.NUM_WIDGET_PROPERTIES), dtype=np.float32)  # TODO: Make this int32?
        
        # Font Variables
        self.font = UIFont()
    
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

    def initialize_widgets(self, widgets: List[ui_utils.GUIWidgetNode], theme: dict):
        
        self.widget_types = np.zeros((len(widgets), ), dtype=np.int32)
        self.widget_num_children = np.zeros((len(widgets), ), dtype=np.int32)
        self.widget_properties = np.zeros((len(widgets), UIWindow.NUM_WIDGET_PROPERTIES), dtype=np.float32)
        self.widget_connections = np.zeros((len(widgets), UIWindow.NUM_WIDGET_CONNECTIONS), dtype=np.int32)
        
        for widget in widgets:
            
            # Type
            self.widget_types[widget.index] = constants.WIDGET_TYPE_MAP[widget.type]
            
            # Padding
            self.widget_properties[widget.index, UIWindow.INDEX_PAD_LEFT] = theme[widget.type]['padding_left']
            self.widget_properties[widget.index, UIWindow.INDEX_PAD_TOP] = theme[widget.type]['padding_top']
            self.widget_properties[widget.index, UIWindow.INDEX_PAD_RIGHT] = theme[widget.type]['padding_right']
            self.widget_properties[widget.index, UIWindow.INDEX_PAD_BOTTOM] = theme[widget.type]['padding_bottom']
            
            # Target size
            width = widget.attributes.get(constants.WIDGET_WIDTH, constants.DEFAULT_WIDGET_SIZE)
            height = widget.attributes.get(constants.WIDGET_HEIGHT, constants.DEFAULT_WIDGET_SIZE)
            self.widget_properties[widget.index, UIWindow.INDEX_TARGET_WIDTH] = width
            self.widget_properties[widget.index, UIWindow.INDEX_TARGET_HEIGHT] = height
            
            # Connections
            self.widget_connections[widget.index, UIWindow.INDEX_PARENT] = widget.parent_index
            self.widget_connections[widget.index, UIWindow.INDEX_NEXT] = widget.next_sibling_index
            self.widget_connections[widget.index, UIWindow.INDEX_PREV] = widget.previous_sibling_index
            self.widget_connections[widget.index, UIWindow.INDEX_FIRST_CHILD] = widget.first_child_index
            
            if widget.parent_index == -1:
                continue
            
            # [Widgets with parents Only] Fixed internal size and Num Children
            self.widget_num_children[widget.parent_index] += 1
            
            target_width = self.widget_properties[widget.index, UIWindow.INDEX_TARGET_WIDTH]
            if target_width > 0:
                self.widget_properties[widget.index, UIWindow.INDEX_SUM_INTERNAL_FIXED_WIDTH] += target_width
            else:
                self.widget_properties[widget.index, UIWindow.INDEX_SUM_INTERNAL_VARIABLE_WIDTH] += target_width
                
            target_height = self.widget_properties[widget.index, UIWindow.INDEX_TARGET_HEIGHT]
            if target_height > 0:
                self.widget_properties[widget.index, UIWindow.INDEX_SUM_INTERNAL_FIXED_HEIGHT] += target_height
            else:
                self.widget_properties[widget.index, UIWindow.INDEX_SUM_INTERNAL_VARIABLE_HEIGHT] += target_height
    
    def update_widgets(self):
        
        # =========================================================
        #                       Update Size
        # =========================================================
        for widget_index in range(self.widget_properties.shape[0]):
            
            # Root widget
            if self.widget_connections[widget_index, UIWindow.INDEX_PARENT] == -1:
                
                padding = self.widget_properties[widget_index, UIWindow.INDEX_PAD_LEFT] + \
                          self.widget_properties[widget_index, UIWindow.INDEX_PAD_RIGHT]
                self.widget_properties[widget_index, UIWindow.INDEX_WIDTH] = self.window_width - padding
                
                padding = self.widget_properties[widget_index, UIWindow.INDEX_PAD_TOP] + \
                          self.widget_properties[widget_index, UIWindow.INDEX_PAD_BOTTOM]
                self.widget_properties[widget_index, UIWindow.INDEX_HEIGHT] = self.window_height - padding
                continue
            
            self.set_widget_size(
                widget_index=widget_index,
                dimension_index=UIWindow.INDEX_WIDTH,
                dimension_fixed_sum_index=UIWindow.INDEX_SUM_INTERNAL_FIXED_WIDTH,
                dimension_variable_sum_index=UIWindow.INDEX_SUM_INTERNAL_VARIABLE_WIDTH,
                padding_a=self.widget_properties[widget_index, UIWindow.INDEX_PAD_LEFT],
                padding_b=self.widget_properties[widget_index, UIWindow.INDEX_PAD_RIGHT])
            self.set_widget_size(
                widget_index=widget_index,
                dimension_index=UIWindow.INDEX_HEIGHT,
                dimension_fixed_sum_index=UIWindow.INDEX_SUM_INTERNAL_FIXED_HEIGHT,
                dimension_variable_sum_index=UIWindow.INDEX_SUM_INTERNAL_VARIABLE_HEIGHT,
                padding_a=self.widget_properties[widget_index, UIWindow.INDEX_PAD_TOP],
                padding_b=self.widget_properties[widget_index, UIWindow.INDEX_PAD_BOTTOM])
            
            
        # =========================================================
        #                      Update Position
        # =========================================================
        """for widget_index in range(gui_data.parent_index.size):
            
            # Root widget
            if gui_data.parent_index[widget_index] == -1:
                gui_data.position[widget_index, :] = gui_data.target_size[widget_index, :]
                continue"""
            
    def set_widget_size(self, 
                        widget_index: int, 
                        dimension_index: int,
                        dimension_fixed_sum_index: int,
                        dimension_variable_sum_index: int,
                        padding_a: float, 
                        padding_b: float) -> None:
        
        parent_index = self.widget_connections[widget_index, UIWindow.INDEX_PARENT]
        parent_width = self.widget_properties[parent_index, dimension_index]
        parent_internal_fixed_width = self.widget_properties[parent_index, dimension_fixed_sum_index]
        parent_internal_variable_size = self.widget_properties[parent_index, dimension_variable_sum_index]
        parent_available_size = parent_width - (padding_a + padding_b) - parent_internal_fixed_width
        target_size = self.widget_properties[parent_index, UIWindow.INDEX_TARGET_WIDTH]
        
        if target_size < 0:
            self.widget_properties[widget_index, dimension_index] = parent_available_size * (-target_size / parent_internal_variable_size)
        else:
            self.widget_properties[widget_index, dimension_index] = parent_available_size
        
    def set_widget_position(self) -> None:
        pass
      


# ==============================================================
#                         DEBUG
# ==============================================================

def main():
    window = UIWindow()
    window.load(
        blueprint_xml_fpath="D:\\git_repositories\\alexandrepv\\gui_framework\\data\\blueprints\\gui_blueprint_2.xml",
        window_id="main_window",
        theme_json_fpath="D:\\git_repositories\\alexandrepv\\gui_framework\\data\\themes\\default_theme.json"
    )

if __name__ == "__main__":
    main()
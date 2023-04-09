import os
import sys
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))

import copy
import string
import numpy as np
import json
from bs4 import BeautifulSoup
import freetype
from typing import List, Union, Tuple

from ui.ui_window_blueprint import UIWindowBlueprint
import ui.ui_window_utils as ui_utils
from core import constants as const

class UIWindow:
    
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
        self.font_texture = np.ndarray((0, 0), dtype=np.float32) 
        self.font_vertices = np.ndarray((0, 0), dtype=np.float32) 
        self.font_uvs = np.ndarray((0, 0), dtype=np.float32) 
        self.font_y_offsets = np.ndarray((0, 0), dtype=np.float32) 
        self.font_x_advances = np.ndarray((0, 0), dtype=np.float32)
    
    def load(self, xml_fpath: str, window_id: str, theme_json_fpath: str):
        
        # Load UI theme
        with open(theme_json_fpath, 'r') as file:
            self.theme = json.load(file)
            face = freetype.Face(self.theme['font']['filepath'])
            glyphs = self.font_generate_glyphs(freefont_face=face)
            self.font_texture = self.font_generate_texture(glyths=glyphs)
            self.font_vertices, self.font_uvs, self.font_y_offsets, self.font_x_advances = self.font_generate_vertices_uvs_offset_advances(glyphs=glyphs)

        # Load UI window blueprint
        with open(xml_fpath) as file:
            root_soup = BeautifulSoup(file.read(), features="html.parser")
            
            # Get window with specified ID
            window_soup = root_soup.find(attrs={'id': window_id})
            if window_soup is None:
                raise ValueError(f"[ERROR] Could not find blueprint for window {window_id}")
            
            widget_pre_node_list = ui_utils.generate_widget_preprocessed_node_list(window_soup=window_soup)
            widget_index_map = ui_utils.generate_widget_index_map(widget_pre_node_list=widget_pre_node_list, 
                                                                  window_id=window_id)
            widgets = ui_utils.generate_widget_node_list(widget_pre_node_list=widget_pre_node_list, 
                                                         widget_index_map=widget_index_map)
            self.initialize_widgets(widgets=widgets, theme=self.theme)
            self.update_widgets()
            
        g = 0
    
    def initialize_widgets(self, widgets: List[ui_utils.GUIWidgetNode], theme: dict):
        
        self.widget_types = np.zeros((len(widgets), ), dtype=np.int32)
        self.widget_num_children = np.zeros((len(widgets), ), dtype=np.int32)
        self.widget_properties = np.zeros((len(widgets), UIWindow.NUM_WIDGET_PROPERTIES), dtype=np.float32)
        self.widget_connections = np.zeros((len(widgets), UIWindow.NUM_WIDGET_CONNECTIONS), dtype=np.int32)
        
        for widget in widgets:
            
            # Type
            self.widget_types[widget.index] = const.WIDGET_TYPE_MAP[widget.type]
            
            # Padding
            self.widget_properties[widget.index, UIWindow.INDEX_PAD_LEFT] = theme[widget.type]['padding_left']
            self.widget_properties[widget.index, UIWindow.INDEX_PAD_TOP] = theme[widget.type]['padding_top']
            self.widget_properties[widget.index, UIWindow.INDEX_PAD_RIGHT] = theme[widget.type]['padding_right']
            self.widget_properties[widget.index, UIWindow.INDEX_PAD_BOTTOM] = theme[widget.type]['padding_bottom']
            
            # Target size
            width = widget.attributes.get(const.WIDGET_WIDTH, const.DEFAULT_WIDGET_SIZE)
            height = widget.attributes.get(const.WIDGET_HEIGHT, const.DEFAULT_WIDGET_SIZE)
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
        parent_width =  self.widget_properties[parent_index, dimension_index]
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
      
    def font_generate_glyphs(self, freefont_face: freetype.Face) -> dict:

        glyphs = dict()
        for unicode_char in string.printable:
            char_int_value = ord(unicode_char)
            freefont_face.load_char(unicode_char)
            glyphs[unicode_char] = {
                "unicode_char": unicode_char,
                "sheet_row": char_int_value // const. FONT_SHEET_COLS,
                "sheet_col": char_int_value % const. FONT_SHEET_COLS,
                "width": int(freefont_face.glyph.bitmap.width),
                "height": int(freefont_face.glyph.bitmap.rows),
                "buffer": np.array(freefont_face.glyph.bitmap.buffer, dtype=np.uint8),
                "offset_hor_bearing_x": freefont_face.glyph.metrics.horiBearingX // const. FONT_CHAR_SIZE,
                "offset_hor_bearing_y": freefont_face.glyph.metrics.horiBearingY // const. FONT_CHAR_SIZE,
                "offset_hor_advance": freefont_face.glyph.metrics.horiAdvance // const. FONT_CHAR_SIZE,
                "offset_ver_bearing_x": freefont_face.glyph.metrics.vertBearingX // const. FONT_CHAR_SIZE,
                "offset_ver_bearing_y": freefont_face.glyph.metrics.vertBearingY // const. FONT_CHAR_SIZE,
                "offset_ver_advance": freefont_face.glyph.metrics.vertAdvance // const. FONT_CHAR_SIZE
                }
        
        return glyphs
    
    def font_generate_texture(self, glyths: dict) -> np.ndarray:
        
        """
        This function generates a "sprite sheet" of the function as an image (texture)

        Returns
        -------
        _type_
            _description_
        """
        
        texture_size_rc = (const. FONT_TEXTURE_HEIGHT, const. FONT_TEXTURE_WIDTH)
        font_texture = np.zeros(texture_size_rc, dtype=np.uint8)

        for _, glyth in glyths.items():

            x0 = glyth['sheet_col'] * const. FONT_SHEET_CELL_WIDTH
            x1 = x0 + glyth['width']
            y0 = glyth['sheet_row'] * const. FONT_SHEET_CELL_HEIGHT
            y1 = y0 + glyth['height']

            glyph_size_pixels = (glyth['height'], glyth['width'])
            font_texture[y0:y1, x0:x1] = np.reshape(glyth['buffer'], glyph_size_pixels)
            
        return font_texture

    def font_generate_vertices_uvs_offset_advances(sel, glyphs: dict):
        
        # Allocate memory for the output vertices
        vertices = np.zeros((const. FONT_NUM_GLYPHS, const. FONT_NUM_VERTICES_PER_CHAR), dtype=np.float32)
        uvs = np.zeros((const. FONT_NUM_GLYPHS, const. FONT_NUM_VERTICES_PER_CHAR), dtype=np.float32)
        y_offsets = np.zeros((const. FONT_NUM_GLYPHS,), dtype=np.float32)
        x_advances = np.zeros((const. FONT_NUM_GLYPHS,), dtype=np.float32)

        for char in string.printable:

            current_glyph = glyphs[char]
            char_decimal = ord(char)

            char_cell_row = char_decimal // const. FONT_SHEET_COLS
            char_cell_col = char_decimal % const. FONT_SHEET_COLS

            # TODO: Make creating the rectangle vertices a function on its own! Avoid code repetition!
            x_min = 0
            x_max = current_glyph['width']
            y_min = -(current_glyph['offset_hor_bearing_y'] // 2)
            y_max = y_min + current_glyph['height']

            a_x, a_y = x_min, y_max
            b_x, b_y = x_max, y_max
            c_x, c_y = x_min, y_min
            d_x, d_y = x_max, y_min

            vertices[char_decimal, :] = (c_x, c_y, b_x, b_y, a_x, a_y, 
                                         c_x, c_y, d_x, d_y, b_x, b_y)

            u_min = (char_cell_col * const. FONT_SHEET_CELL_WIDTH) / const. FONT_TEXTURE_WIDTH
            u_max = (u_min + current_glyph['width']) / const. FONT_TEXTURE_WIDTH
            v_min = (char_cell_row * const. FONT_SHEET_CELL_HEIGHT) / const. FONT_TEXTURE_HEIGHT
            v_max = (v_min + current_glyph['height']) / const. FONT_TEXTURE_HEIGHT

            a_x, a_y = u_min, v_max
            b_x, b_y = u_max, v_max
            c_x, c_y = u_min, v_min
            d_x, d_y = u_max, v_min

            uvs[char_decimal, :] = (c_x, c_y, b_x, b_y, a_x, a_y, 
                                    c_x, c_y, d_x, d_y, b_x, b_y)

            y_offsets[char_decimal] = current_glyph['offset_hor_bearing_y']
            x_advances[char_decimal] = current_glyph['width']

        return vertices, uvs, y_offsets, x_advances

# ==============================================================
#                         DEBUG
# ==============================================================

def main():
    window = UIWindow()
    window.load(
        xml_fpath="D:\\git_repositories\\alexandrepv\\gui_framework\\data\\blueprints\\gui_blueprint_2.xml",
        window_id="main_window",
        theme_json_fpath="D:\\git_repositories\\alexandrepv\\gui_framework\\data\\themes\\default_theme.json"
    )

if __name__ == "__main__":
    main()
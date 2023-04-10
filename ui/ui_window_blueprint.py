import copy
import json
import string
import numpy as np
import freetype
from dataclasses import dataclass
from bs4 import BeautifulSoup
from typing import List, Tuple


from core import constants as const

@dataclass
class GUIWidgetNodePreProcessed:
    id: str
    parent_id: str
    next_sibling_id: str
    previous_sibling_id: str
    first_child_id: str
    horizontal_align: int
    vertical_align: int
    type: str
    attributes: dict
    
@dataclass
class GUIWidgetNode:
    index: int
    parent_index: int
    next_sibling_index: int
    previous_sibling_index: int
    first_child_index: int
    num_children: int
    horizontal_align: int
    vertical_align: int
    type: str
    attributes: dict
    
class UIWindowBlueprint:
    
    __slots__ = ('theme',
                 'widgets',
                 'font_texture',
                 'font_vertices',
                 'font_uvs',
                 'font_y_offsets',
                 'font_x_advances')
    
    def __init__(self) -> None:
        
        # Styles
        self.theme = None
        
        # Widgets and other elements
        self.widgets = []
        
        # Font Variables
        self.font_texture = np.ndarray((0, 0), dtype=np.float32) 
        self.font_vertices = np.ndarray((0, 0), dtype=np.float32) 
        self.font_uvs = np.ndarray((0, 0), dtype=np.float32) 
        self.font_y_offsets = np.ndarray((0, 0), dtype=np.float32) 
        self.font_x_advances = np.ndarray((0, 0), dtype=np.float32) 
        
    # =========================================================================
    #                             Getters
    # =========================================================================
    
    @property
    def num_widgets(self):
        return len(self.widgets)
    
    @property
    def num_styles(self):
        return len(self.styles)
    
    # =========================================================================
    #                             Core functions
    # =========================================================================
    
    def load(self, xml_fpath: str, theme_json_fpath: str) -> list:

        # Load GUI theme
        with open(theme_json_fpath, 'r') as file:
            self.theme = json.load(file)

            # TODO: Re-organise how the font is loaded
            face = freetype.Face(self.theme['font']['filepath'])
            glyphs = self.font_generate_glyphs(freefont_face=face)
            self.font_texture = self.font_generate_texture(glyths=glyphs)
            self.font_vertices, self.font_uvs, self.font_y_offsets, self.font_x_advances = self.font_generate_vertices_uvs_offset_advances(glyphs=glyphs)

        # Load GUI blueprint
        with open(xml_fpath) as file:
            soup = BeautifulSoup(file.read(), features="html.parser")
            widget_pre_node_list = self.generate_widget_preprocessed_node_list(soup=soup)
            widget_index_map = self.generate_widget_index_map(widget_pre_node_list=widget_pre_node_list)
            self.widgets = self.generate_widget_node_list(widget_pre_node_list=widget_pre_node_list, 
                                                                widget_index_map=widget_index_map)
            
    def generate_widget_preprocessed_node_list(self, soup: BeautifulSoup) -> list:
        
        # Locate root node, the window
        window_soup = soup.find("window", recursive=False)
        if window_soup is None:
            raise ValueError('[ERROR] Could not find')
        
        # Recursive function
        def _build_node_list(soup_node, node_list: list):

            next_sibling = soup_node.find_next_sibling()
            previous_sibling = soup_node.find_previous_sibling()
            children_list = soup_node.findChildren(recursive=False)
            
            parent_id = soup_node.parent.attrs[const.WIDGET_ID] if const.WIDGET_ID in soup_node.parent.attrs else None
            next_sibling_id = next_sibling.attrs[const.WIDGET_ID] if next_sibling is not None else None
            previous_sibling_id = previous_sibling.attrs[const.WIDGET_ID] if previous_sibling is not None else None
            first_child_id = children_list[0].attrs[const.WIDGET_ID] if len(children_list) > 0 else None
            
            horizontal_align = soup_node.parent.attrs[const.WIDGET_H_ALIGN] if const.WIDGET_H_ALIGN in soup_node.parent.attrs else const.ALIGN_CENTER
            vertical_align = soup_node.parent.attrs[const.WIDGET_V_ALIGN] if const.WIDGET_V_ALIGN in soup_node.parent.attrs else const.ALIGN_CENTER

            node_list.append(
                GUIWidgetNodePreProcessed(
                    id=soup_node.attrs[const.WIDGET_ID],
                    parent_id=parent_id,
                    next_sibling_id=next_sibling_id,
                    previous_sibling_id=previous_sibling_id,
                    first_child_id=first_child_id,
                    horizontal_align=horizontal_align,
                    vertical_align=vertical_align,
                    type=soup_node.name,
                    attributes=soup_node.attrs)
                )
            
            children = soup_node.findChildren(recursive=False)
            if len(children) == 0:
                return

            for child in children:
                _build_node_list(soup_node=child, node_list=node_list)

        widget_node_list = []
        _build_node_list(soup_node=window_soup, node_list=widget_node_list)
        
        return widget_node_list
    
    def generate_widget_index_map(self, widget_pre_node_list: list) -> dict:
        
        map = dict()
        for index, widget_node in enumerate(widget_pre_node_list):
            
            if widget_node.id in map:
                raise ValueError(f"[ERROR] Widget ID '{widget_node.id}' duplicated. Please make sure that each widget has a unique ID.")
            
            map[widget_node.id] = index
        
        # Edge Case: Root node has "None" for parent_id 
        map[None] = -1
            
        return map
    
    def generate_widget_node_list(self, widget_pre_node_list: list, widget_index_map: dict) -> list:
        
        # Stage 1) Convert id string values to indices and values in strings to floats
        widgets = []
        for node in widget_pre_node_list:
            widgets.append(
                GUIWidgetNode(
                    index=widget_index_map[node.id],
                    parent_index=widget_index_map[node.parent_id],
                    next_sibling_index=widget_index_map[node.next_sibling_id],
                    previous_sibling_index=widget_index_map[node.previous_sibling_id],
                    first_child_index=widget_index_map[node.first_child_id],
                    num_children=0,
                    horizontal_align=node.horizontal_align,
                    vertical_align=node.vertical_align,
                    type=node.type,
                    attributes=self.process_attributes(attributes=node.attributes)
                )
            )
          
        # Stage 2) Sort nodes according to parents
        sorted_widgets, _, source_indices = self.arg_sort_widget_node_list(widget_node_list=widgets)
        for index, widget in enumerate(sorted_widgets):
            widget.index = index
            widget.parent_index = source_indices[widget.parent_index] if widget.parent_index != -1 else -1
            widget.next_sibling_index = source_indices[widget.next_sibling_index] if widget.next_sibling_index != -1 else -1
            widget.previous_sibling_index = source_indices[widget.previous_sibling_index] if widget.previous_sibling_index != -1 else -1
            widget.first_child_index = source_indices[widget.first_child_index] if widget.first_child_index != -1 else -1

        # Stage 3) Update number of children
        num_children_sum = np.zeros(len(sorted_widgets), dtype=int)
        for widget in sorted_widgets:
            if widget.parent_index == -1:
                continue
            num_children_sum[widget.parent_index] += 1
            
        for index, widget in enumerate(sorted_widgets):
            widget.num_children = num_children_sum[index]

        return sorted_widgets
        
    def process_attributes(self, attributes: dict) -> dict:
        
        updated_attributes = copy.deepcopy(attributes)
        
        for key, value in attributes.items():
            
            if key not in const.WIDGET_NUMERICAL_IDS:
                updated_attributes[key] = value
                continue
                
            updated_attributes[key] = -float(value[:-1]) / 100.0 if value[-1] == '%' else float(value)
        
        return updated_attributes
    
    # =========================================================================
    #                            Utility functions
    # =========================================================================
    
    def arg_sort_widget_node_list(self, widget_node_list: List[GUIWidgetNode]) -> Tuple[np.array, np.array]:
        """
        Sorts a list by parent and previous sibling values. This ensures that all sibling nodes are kept
        together and sorted from first to last as defined in the original XML file.
        - The DESTINATION indices array contain the location from where those items came from in the original list
        - The SOURCE indices array contain the location where the items from the original list should go in the sorted list
        """
        
        # Sort a copy of the input widget in descending order of parents
        parent_sorted_widgets = copy.deepcopy(widget_node_list)
        parent_sorted_widgets.sort(key=lambda node: (node.parent_index, node.previous_sibling_index)) 
        
        dest_indices = np.array([widget.index for widget in parent_sorted_widgets], dtype=int)
        source_indices = np.zeros(dest_indices.size, dtype=int)
        for i in range(source_indices.size):
            source_indices[dest_indices[i]] = i  
            
        return parent_sorted_widgets, dest_indices, source_indices
    
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
    
    # ===========================================================================
    #                             DEBUG functions
    # ===========================================================================
    
    def debug_print_widget_node_list(self, widget_node_list: List[GUIWidgetNode]) -> None:
        print(f'[ Debug Widgets ]')
        for index, widget in enumerate(widget_node_list):
            a = f"{widget.type} "
            b = f"index={widget.index} "
            c = f"parent={widget.parent_index}"
            d = f"next={widget.next_sibling_index}"
            e = f"prev={widget.previous_sibling_index}"
            f = f"first_child={widget.first_child_index}"
            g = f"num_children={widget.num_children}"
            print(f"[{index}] {a}\t{b}\t{c}\t{d}\t{e}\t{f}\t{g}")
        print('')
            

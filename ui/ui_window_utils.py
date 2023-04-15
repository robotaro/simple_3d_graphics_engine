import numpy as np
import copy
from typing import List, Union, Tuple
from dataclasses import dataclass
from bs4 import BeautifulSoup
from ui import ui_constants as const


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
        
def generate_widget_preprocessed_node_list(window_soup: BeautifulSoup) -> list:
    
    # Locate root node, the window
    first_soup = window_soup.find(recursive=False)
    if first_soup is None:
        raise ValueError('[ERROR] Window soup does not have any children')
    
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
    _build_node_list(soup_node=first_soup, node_list=widget_node_list)
    
    return widget_node_list

def generate_widget_index_map(widget_pre_node_list: list, window_id: str) -> dict:

    
    map = dict()
    for index, widget_node in enumerate(widget_pre_node_list):
        
        if widget_node.id in map:
            raise ValueError(f"[ERROR] Widget ID '{widget_node.id}' duplicated. Please make sure that each widget has a unique ID.")
        
        map[widget_node.id] = index
        
    # Window Node
    map[window_id] = -1
    
    # Edge Case: Root node has "None" for parent_id 
    map[None] = -1
        
    return map

def generate_widget_node_list(widget_pre_node_list: list, widget_index_map: dict) -> list:
    
    # Stage 1) Convert id string values to indices and values in strings to floats
    widgets = []
    for node in widget_pre_node_list:
        widget_node = GUIWidgetNode(
            index=widget_index_map[node.id],
            parent_index=widget_index_map[node.parent_id],
            next_sibling_index=widget_index_map[node.next_sibling_id],
            previous_sibling_index=widget_index_map[node.previous_sibling_id],
            first_child_index=widget_index_map[node.first_child_id],
            num_children=0,
            horizontal_align=node.horizontal_align,
            vertical_align=node.vertical_align,
            type=node.type,
            attributes=process_attributes(attributes=node.attributes)
        )
        widgets.append(widget_node)
        
    # Stage 2) Sort nodes according to parents
    sorted_widgets, _, source_indices = arg_sort_widget_node_list(widget_node_list=widgets)
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

def arg_sort_widget_node_list(widget_node_list: List[GUIWidgetNode]) -> Tuple[np.array, np.array]:
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
    
def process_attributes(attributes: dict) -> dict:
    
    updated_attributes = copy.deepcopy(attributes)
    
    for key, value in attributes.items():
        
        if key not in const.WIDGET_NUMERICAL_IDS:
            updated_attributes[key] = value
            continue
            
        updated_attributes[key] = -float(value[:-1]) / 100.0 if value[-1] == '%' else float(value)
    
    return updated_attributes
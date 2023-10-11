from bs4 import BeautifulSoup
from typing import Union

"""
Series of utility functions designed to help with processing and XML file
"""


def get_attribute_string(soup_node: BeautifulSoup, attribute_name: str) -> Union[str, None]:
    return soup_node.attrs.get(attribute_name, None)


def get_attribute_float(soup_node: BeautifulSoup, attribute_name: str) -> Union[float, None]:
    attribute_str = soup_node.attrs.get(attribute_name, None)
    return float(attribute_str) if attribute_str is not None else None


def get_attribute_int(soup_node: BeautifulSoup, attribute_name: str) -> Union[int, None]:
    attribute_str = soup_node.attrs.get(attribute_name, None)
    return int(attribute_str) if attribute_str is not None else None


def get_attribute_tuple_float(soup: BeautifulSoup, attribute: str) -> Union[tuple, None]:
    position_str = soup.attrs.get(attribute, None)
    if position_str is None:
        return None
    return tuple([float(part) for part in position_str.strip(" ").split(" ")])


def get_attribute_tuple_int(soup: BeautifulSoup, attribute: str) -> Union[tuple, None]:
    position_str = soup.attrs.get(attribute, None)
    if position_str is None:
        return None
    return tuple([int(part) for part in position_str.strip(" ").split(" ")])

import os
import numpy as np
import string
import logging
from typing import Union
from dataclasses import dataclass, field
import freetype

from ecs import constants

@dataclass
class Font:

    texture: np.ndarray = field(default=np.ndarray((0, 0), dtype=np.float32))
    texture: np.ndarray = field(default=np.ndarray((0, 0), dtype=np.float32))
    texture: np.ndarray = field(default=np.ndarray((0, 0), dtype=np.float32))
    texture: np.ndarray = field(default=np.ndarray((0, 0), dtype=np.float32))
    texture: np.ndarray = field(default=np.ndarray((0, 0), dtype=np.float32))
    texture: np.ndarray = field(default=np.ndarray((0, 0), dtype=np.float32))


class FontLibrary:

    def __init__(self, logger: Union[logging.Logger, None]=None):

        self.fonts = {}
        self.logger = logger if logger is not None else logging.Logger

    def load(self, ttf_fpath: str) -> bool:


        font_name = os.path.basename(ttf_fpath)
        new_font = Font(
            texture=
        )

        self.font_texture = np.ndarray((0, 0), dtype=np.float32)
        self.font_vertices = np.ndarray((0, 0), dtype=np.float32)
        self.font_uvs = np.ndarray((0, 0), dtype=np.float32)
        self.font_y_offsets = np.ndarray((0, 0), dtype=np.float32)
        self.font_x_advances = np.ndarray((0, 0), dtype=np.float32)

        glyphs = self.generate_glyphs(font_ttf_fpath=ttf_fpath)
        self.font_texture = self.generate_texture(glyths=glyphs)
        output = self.generate_vertices_uvs_offset_advances(glyphs=glyphs)
        (self.font_vertices, self.font_uvs, self.font_y_offsets, self.font_x_advances) = output

        self._font_loaded = True
        return True

    @property
    def __getitem__(self, item):
        return self.fonts

    @staticmethod
    def generate_glyphs(font_ttf_fpath: str) -> dict:

        # Check if file exists
        if not os.path.isfile(font_ttf_fpath):
            raise FileNotFoundError(f"[ERROR] Font file '{font_ttf_fpath}' not found")

        # Load font and set initial size
        face = freetype.Face(font_ttf_fpath)
        face.set_char_size(constants.FONT_CHAR_SIZE ** 2)

        # Generate glyp look-up dictionary
        glyphs = dict()
        for unicode_char in string.printable:
            char_int_value = ord(unicode_char)
            face.load_char(unicode_char)
            glyphs[unicode_char] = {
                "unicode_char": unicode_char,
                "sheet_row": char_int_value // constants.FONT_SHEET_COLS,
                "sheet_col": char_int_value % constants.FONT_SHEET_COLS,
                "width": int(face.glyph.bitmap.width),
                "height": int(face.glyph.bitmap.rows),
                "buffer": np.array(face.glyph.bitmap.buffer, dtype=np.uint8),
                "offset_hor_bearing_x": face.glyph.metrics.horiBearingX // constants.FONT_CHAR_SIZE,
                "offset_hor_bearing_y": face.glyph.metrics.horiBearingY // constants.FONT_CHAR_SIZE,
                "offset_hor_advance": face.glyph.metrics.horiAdvance // constants.FONT_CHAR_SIZE,
                "offset_ver_bearing_x": face.glyph.metrics.vertBearingX // constants.FONT_CHAR_SIZE,
                "offset_ver_bearing_y": face.glyph.metrics.vertBearingY // constants.FONT_CHAR_SIZE,
                "offset_ver_advance": face.glyph.metrics.vertAdvance // constants.FONT_CHAR_SIZE
            }

        return glyphs

    @staticmethod
    def generate_texture(glyths: dict) -> np.ndarray:
        """
        This function generates a "sprite sheet" of the function as an image (texture)
        :param glyths: Dictionary of glyphs created by
        :return:
        """

        texture_size_rc = (constants.FONT_TEXTURE_HEIGHT, constants.FONT_TEXTURE_WIDTH)
        font_texture = np.zeros(texture_size_rc, dtype=np.uint8)

        for _, glyth in glyths.items():
            x0 = glyth['sheet_col'] * constants.FONT_SHEET_CELL_WIDTH
            x1 = x0 + glyth['width']
            y0 = glyth['sheet_row'] * constants.FONT_SHEET_CELL_HEIGHT
            y1 = y0 + glyth['height']

            glyph_size_pixels = (glyth['height'], glyth['width'])
            font_texture[y0:y1, x0:x1] = np.reshape(glyth['buffer'], glyph_size_pixels)

        return font_texture

    @staticmethod
    def generate_vertices_uvs_offset_advances(glyphs: dict):

        # Allocate memory for the output vertices
        vertices = np.zeros((constants.FONT_NUM_GLYPHS, constants.FONT_NUM_VERTICES_PER_CHAR), dtype=np.float32)
        uvs = np.zeros((constants.FONT_NUM_GLYPHS, constants.FONT_NUM_VERTICES_PER_CHAR), dtype=np.float32)
        y_offsets = np.zeros((constants.FONT_NUM_GLYPHS,), dtype=np.float32)
        x_advances = np.zeros((constants.FONT_NUM_GLYPHS,), dtype=np.float32)

        for char in string.printable:
            current_glyph = glyphs[char]
            char_decimal = ord(char)

            char_cell_row = char_decimal // constants.FONT_SHEET_COLS
            char_cell_col = char_decimal % constants.FONT_SHEET_COLS

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

            u_min = (char_cell_col * constants.FONT_SHEET_CELL_WIDTH) / constants.FONT_TEXTURE_WIDTH
            u_max = (u_min + current_glyph['width']) / constants.FONT_TEXTURE_WIDTH
            v_min = (char_cell_row * constants.FONT_SHEET_CELL_HEIGHT) / constants.FONT_TEXTURE_HEIGHT
            v_max = (v_min + current_glyph['height']) / constants.FONT_TEXTURE_HEIGHT

            a_x, a_y = u_min, v_max
            b_x, b_y = u_max, v_max
            c_x, c_y = u_min, v_min
            d_x, d_y = u_max, v_min

            uvs[char_decimal, :] = (c_x, c_y, b_x, b_y, a_x, a_y,
                                    c_x, c_y, d_x, d_y, b_x, b_y)

            x_advances[char_decimal] = current_glyph['width']
            y_offsets[char_decimal] = current_glyph['offset_hor_bearing_y']

        return vertices, uvs, y_offsets, x_advances

    def generate_text_vertices_and_uvs(self, text: str, x_offset: float, y_offset: float):
        """
        Once the font is loaded, you can use this function to generate a list of tuples containing the vertices
        and UV locations for all characters in the text

        :param text: str, Input text that you want to convert to characters to be rendered
        :param x_offset: float, horizontal offset where the left side of the first character should appear
        :param y_offset: float, vertical offset where the base line of the text should appear.
        :return: list
        """

        # TODO: This function needs to be "Numbafied", and final output text must be common memory space

        if not self._font_loaded:
            raise Exception("[ERROR] Font not loaded. Please load a font before generating the vertices and UVs.")

        num_chars = len(text)

        vertices = np.ndarray((num_chars, 12), dtype=np.float32)
        uvs = np.ndarray((num_chars, 12), dtype=np.float32)
        for index, char in enumerate(text):
            char_decimal = ord(char)
            vertices[index, :] = self.font_vertices[char_decimal, :]
            uvs[index, :] = self.font_uvs[char_decimal, :]

        return vertices, uvs


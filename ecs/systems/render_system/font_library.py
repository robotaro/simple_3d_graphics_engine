import os
import numpy as np
import string
import logging
from typing import Union
from dataclasses import dataclass, field
import freetype
import moderngl

from ecs import constants

@dataclass
class Font:

    name: str = field(default="unnamed_font")
    texture_data: np.ndarray = field(default=np.ndarray((0, 0), dtype=np.float32))
    texture_vbo: moderngl.Buffer = field(default=None)
    character_data: np.ndarray = field(default=np.ndarray((0, 0), dtype=np.float32))


class FontLibrary:

    __slots__ = [
        "ctx",
        "fonts",
        "logger"
    ]

    def __init__(self,
                 context: moderngl.Context,
                 font_directory=constants.FONTS_DIR,
                 logger: Union[logging.Logger, None] = None):

        """
        Keep in mind:

        "Sample string to render!".encode('iso-8859-1', errors='replace')

        :param logger:
        """
        self.ctx = context
        self.fonts = {}
        self.logger = logger if logger is not None else logging.Logger

        if font_directory is not None:
            ttf_fpaths = [os.path.join(font_directory, filename)
                          for filename in os.listdir(font_directory) if filename.endswith(".ttf")]
            for fpath in ttf_fpaths:
                self.load(ttf_fpath=fpath)

    def load(self, ttf_fpath: str) -> bool:

        glyphs = self.generate_glyphs(font_ttf_fpath=ttf_fpath)
        new_font = Font()
        new_font.name = os.path.basename(ttf_fpath)
        new_font.texture_data = self.generate_texture(glyths=glyphs)
        new_font.texture_data = new_font.texture_data.astype('f4') / 255.0
        new_font.texture_vbo = self.ctx.texture(size=new_font.texture_data.shape,
                                                data=new_font.texture_data.tobytes(),
                                                components=1,
                                                dtype='f4')
        new_font.character_data = self.generate_font_parameters(glyphs=glyphs)
        self.fonts[new_font.name] = new_font

        return True

    def generate_text_vbo_data(self, font_name: str, text: str) -> np.ndarray:
        font_parameters = self.fonts[font_name].character_data

        # TODO: Optimise this with numba
        text_data = np.ndarray((len(text), constants.FONT_LIBRARY_NUM_PARAMETERS), dtype=np.float32)
        for index, char in enumerate(text):
            char_index = ord(char)
            text_data[index, :] = font_parameters[char_index, :]

        return text_data

    @staticmethod
    def generate_glyphs(font_ttf_fpath: str) -> dict:

        # Check if file exists
        if not os.path.isfile(font_ttf_fpath):
            raise FileNotFoundError(f"[ERROR] Font file '{font_ttf_fpath}' not found")

        # Load font and set initial size
        face = freetype.Face(font_ttf_fpath)
        face.set_char_size(constants.FONT_CHAR_SIZE ** 2)

        # Generate glypH look-up dictionary
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
    def generate_font_parameters(glyphs: dict) -> np.ndarray:

        # Allocate memory for all glyphy parameters
        data = np.ndarray((constants.FONT_LIBRARY_NUM_CHARACTERS,
                           constants.FONT_LIBRARY_NUM_PARAMETERS), dtype=np.float32)

        for char in string.printable:
            selected_glyph = glyphs[char]
            char_index = ord(char)

            char_cell_row = char_index // constants.FONT_SHEET_COLS
            char_cell_col = char_index % constants.FONT_SHEET_COLS

            data[char_index, constants.FONT_LIBRARY_COLUMN_INDEX_X] = 0
            data[char_index, constants.FONT_LIBRARY_COLUMN_INDEX_Y] = -(selected_glyph['offset_hor_bearing_y'] // 2)
            data[char_index, constants.FONT_LIBRARY_COLUMN_INDEX_WIDTH] = selected_glyph['width']
            data[char_index, constants.FONT_LIBRARY_COLUMN_INDEX_HEIGHT] = selected_glyph['height']

            u_min = (char_cell_col * constants.FONT_SHEET_CELL_WIDTH) / constants.FONT_TEXTURE_WIDTH
            u_max = (u_min + selected_glyph['width']) / constants.FONT_TEXTURE_WIDTH
            v_min = (char_cell_row * constants.FONT_SHEET_CELL_HEIGHT) / constants.FONT_TEXTURE_HEIGHT
            v_max = (v_min + selected_glyph['height']) / constants.FONT_TEXTURE_HEIGHT

            data[char_index, constants.FONT_LIBRARY_COLUMN_INDEX_U_MIN] = u_min
            data[char_index, constants.FONT_LIBRARY_COLUMN_INDEX_V_MIN] = u_max
            data[char_index, constants.FONT_LIBRARY_COLUMN_INDEX_U_MAX] = v_min
            data[char_index, constants.FONT_LIBRARY_COLUMN_INDEX_V_MAX] = v_max

            data[char_index, constants.FONT_LIBRARY_COLUMN_INDEX_HORIZONTAL_ADVANCE] = selected_glyph['width']  # TODO: Really?
            data[char_index, constants.FONT_LIBRARY_COLUMN_INDEX_VERTICAL_OFFSET] = selected_glyph['offset_hor_bearing_y']

        return data

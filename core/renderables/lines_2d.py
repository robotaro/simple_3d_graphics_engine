import numpy as np
import moderngl

from core.node import Node
from core.material import Material
from core.utilities import utils_decorators


class Lines2D(Node):
    """Render 2D lines."""

    def __init__(
        self,
        lines,
        color=(0.0, 0.0, 1.0, 1.0),
        mode="line_strip",
        **kwargs,
    ):
        """
        Initializer.
        :param lines: Set of 3D coordinates as a np array of shape (F, L, 3) or (L, 3).
        :param color: Color of the line (4-tuple) or array of color (N_LINES, 4), one for each line.
        :param mode: 'lines' or 'line_strip'.
            'lines': a line is drawn from point 0 to 1, from 2 to 3, and so on, number of lines is L / 2.
            'line_strip': a line is drawn between all adjacent points, 0 to 1, 1 to 2 and so on, number of lines is L - 1.
        """
        if len(lines.shape) == 2:
            lines = lines[np.newaxis]
        assert len(lines.shape) == 3
        assert mode == "lines" or mode == "line_strip"
        if mode == "lines":
            assert lines.shape[1] % 2 == 0

        self._lines = lines
        self.mode = mode
        self.n_lines = self.lines.shape[1] // 2 if mode == "lines" else self.lines.shape[1] - 1
        self.is_renderable = False

        # Define a default material in case there is None.
        if isinstance(color, tuple) or len(color.shape) == 1:
            kwargs["material"] = kwargs.get("material", Material(color_rgb=color, ambient=0.2))
            self.line_colors = kwargs["material"].color
        else:
            assert (
                color.shape[1] == 4 and color.shape[0] == self.n_lines
            ), "Color must be a tuple of 4 values or a numpy array of shape (N_LINES, 4)"
            self.line_colors = color

        super(Lines2D, self).__init__(**kwargs)

    @property
    def bounds(self):
        bounds = self.get_bounds(self.lines)
        return bounds

    @property
    def current_bounds(self):
        bounds = self.get_bounds(self.current_lines)
        return bounds

    @property
    def lines(self):
        return self._lines

    @lines.setter
    def lines(self, value):
        self._lines = value if len(value.shape) == 3 else value[np.newaxis]
        self.n_frames = self.lines.shape[0]
        self.redraw()

    @property
    def current_lines(self):
        idx = self.current_frame_id if self._lines.shape[0] > 1 else 0
        return self._lines[idx]

    @current_lines.setter
    def current_lines(self, lines):
        assert len(lines.shape) == 2
        idx = self.current_frame_id if self._lines.shape[0] > 1 else 0
        self._lines[idx] = lines
        self.redraw()

    @Node.color.setter
    def color(self, color):
        self.material.color = color
        self.line_colors = color
        self.redraw()

    @property
    def line_colors(self):
        if len(self._line_colors.shape) == 1:
            t = np.tile(np.array(self._line_colors), (self.n_lines, 1))
            return t
        else:
            return self._line_colors

    @line_colors.setter
    def line_colors(self, color):
        if isinstance(color, tuple):
            color = np.array(color)
        self._line_colors = color
        self.redraw()

    def on_frame_update(self):
        super().on_frame_update()
        self.redraw()

    def _get_vertices(self):
        vertices = self.current_lines
        if self.mode == "line_strip":
            expanded = np.zeros((self.n_lines * 2, 3))
            expanded[::2] = vertices[:-1]
            expanded[1::2] = vertices[1:]
            vertices = expanded
        return vertices

    def _get_colors(self):
        cols = self.line_colors
        doubled = np.zeros((self.n_lines * 2, 4))
        doubled[::2] = cols
        doubled[1::2] = cols
        return doubled

    def redraw(self, **kwargs):
        """Upload the current frame data to the GPU for rendering."""
        if not self.is_renderable:
            return

        self.vbo_vertices.write(self._get_vertices().astype("f4").tobytes())
        self.vbo_colors.write(self._get_colors().astype("f4").tobytes())

    @Node.once
    def make_renderable(self, ctx: moderngl.Context):
        self.prog = get_simple_unlit_program()

        self.vbo_vertices = ctx.buffer(self._get_vertices().astype("f4").tobytes(), dynamic=True)
        self.vbo_colors = ctx.buffer(self._get_colors().astype("f4").tobytes(), dynamic=True)
        self.vao = VAO("lines", mode=moderngl.LINES)
        self.vao.buffer(self.vbo_vertices, "3f", ["in_position"])
        self.vao.buffer(self.vbo_colors, "4f", ["in_color"])

    def render(self, camera, **kwargs):
        self.set_camera_matrices(self.prog, camera, **kwargs)
        self.vao.render(self.prog, vertices=self.n_lines * 2)

    @utils_decorators.hooked
    def release(self):
        if self.is_renderable:
            self.vao.release()
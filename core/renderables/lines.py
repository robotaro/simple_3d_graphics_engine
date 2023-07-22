
import moderngl
import numpy as np
from moderngl_window.opengl.vao import VAO

from core.geometry_3d import shapes_3d
from core.utilities import utils_decorators
from core.node import Node
from core.material import Material


class Lines(Node):
    """Render lines as cylinders or cones. Can render approx. 600k lines at 40 fps."""

    def __init__(
        self,
        lines,
        radius_base=0.01,
        r_tip=None,
        color=(0.0, 0.0, 1.0, 1.0),
        mode="line_strip",
        cast_shadow=True,
        **kwargs,
    ):
        """
        Initializer.
        :param lines: Set of 3D coordinates as a np array of shape (F, L, 3) or (L, 3).
        :param radius_base: Thickness of the line.
        :param r_tip: If set, the thickness of the line will taper from r_base to r_tip. If set to 0.0 it will create
          a proper cone.
        :param color: Color of the line (4-tuple) or array of color (N_LINES, 4), one for each line.
        :param mode: 'lines' or 'line_strip'.
            'lines': a line is drawn from point 0 to 1, from 2 to 3, and so on, number of lines is L / 2.
            'line_strip': a line is drawn between all adjacent points, 0 to 1, 1 to 2 and so on, number of lines is L - 1.
        :param cast_shadow: If True the mesh casts a shadow on other objects.
        """
        if len(lines.shape) == 2:
            lines = lines[np.newaxis]
        assert len(lines.shape) == 3
        assert mode == "lines" or mode == "line_strip"
        if mode == "lines":
            assert lines.shape[1] % 2 == 0

        self._lines = lines
        self.mode = mode
        self.r_base = radius_base
        self.r_tip = r_tip if r_tip is not None else radius_base

        self.vertices, self.faces = self.get_mesh()
        self.n_lines = self.lines.shape[1] // 2 if mode == "lines" else self.lines.shape[1] - 1

        # Define a default material in case there is None.
        if isinstance(color, tuple) or len(color.shape) == 1:
            kwargs["material"] = kwargs.get("material", Material(color=color, ambient=0.2))
            self.line_colors = kwargs["material"].color
        else:
            assert (
                color.shape[1] == 4 and color.shape[0] == self.n_lines
            ), "Color must be a tuple of 4 values or a numpy array of shape (N_LINES, 4)"
            self.line_colors = color

        super(Lines, self).__init__(**kwargs)

        self._need_upload = True
        self.draw_edges = False

        # Render passes.
        self.outline = True
        self.fragmap = True
        self.depth_prepass = True
        self.cast_shadow = cast_shadow

    @property
    def bounds(self):
        bounds = self.get_bounds(self.lines)
        r = max(self.r_base, self.r_tip)
        bounds[:, 0] -= r
        bounds[:, 1] += r
        return bounds

    @property
    def current_bounds(self):
        bounds = self.get_bounds(self.current_lines)
        r = max(self.r_base, self.r_tip)
        bounds[:, 0] -= r
        bounds[:, 1] += r
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
        self.redraw()

    def redraw(self, **kwargs):
        self._need_upload = True

    @Node.once
    def make_renderable(self, ctx: moderngl.Context):
        self.prog = get_lines_instanced_program()

        vs_path = "lines_instanced_positions.vs.glsl"
        self.outline_program = get_outline_program(vs_path)
        self.depth_only_program = get_depth_only_program(vs_path)
        self.fragmap_program = get_fragmap_program(vs_path)

        self.vbo_vertices = ctx.buffer(self.vertices.astype("f4").tobytes())
        self.vbo_indices = ctx.buffer(self.faces.astype("i4").tobytes())
        self.vbo_instance_base = ctx.buffer(reserve=self.n_lines * 12)
        self.vbo_instance_tip = ctx.buffer(reserve=self.n_lines * 12)
        self.vbo_instance_color = ctx.buffer(reserve=self.n_lines * 16)

        self.vao = VAO()
        self.vao.buffer(self.vbo_vertices, "3f4", "in_position")
        self.vao.buffer(self.vbo_instance_base, "3f4/i", "instance_base")
        self.vao.buffer(self.vbo_instance_tip, "3f4/i", "instance_tip")
        self.vao.buffer(self.vbo_instance_color, "4f4/i", "instance_color")
        self.vao.index_buffer(self.vbo_indices)

    def _upload_buffers(self):
        if not self.is_renderable or not self._need_upload:
            return
        self._need_upload = False

        lines = self.current_lines
        if self.mode == "lines":
            v0s = lines[::2]
            v1s = lines[1::2]
        else:
            v0s = lines[:-1]
            v1s = lines[1:]

        self.vbo_instance_base.write(v0s.astype("f4").tobytes())
        self.vbo_instance_tip.write(v1s.astype("f4").tobytes())

        if len(self._line_colors.shape) > 1:
            self.vbo_instance_color.write(self._line_colors.astype("f4").tobytes())

    def render(self, camera, **kwargs):
        self._upload_buffers()

        prog = self.prog
        prog["r_base"] = self.r_base
        prog["r_tip"] = self.r_tip
        if len(self._line_colors.shape) == 1:
            prog["use_uniform_color"] = True
            prog["uniform_color"] = tuple(self.color)
        else:
            prog["use_uniform_color"] = False
        prog["draw_edges"].value = 1.0 if self.draw_edges else 0.0
        prog["win_size"].value = kwargs["window_size"]
        prog["clip_control"].value = (0, 0, 0)

        self.set_camera_matrices(prog, camera, **kwargs)
        set_lights_in_program(
            prog,
            kwargs["lights"],
            kwargs["shadows_enabled"],
            kwargs["ambient_strength"],
        )
        set_material_properties(prog, self.material)
        self.receive_shadow(prog, **kwargs)
        self.vao.render(prog, moderngl.TRIANGLES, instances=self.n_lines)

    def render_positions(self, prog):
        if self.is_renderable:
            self._upload_buffers()
            prog["r_base"] = self.r_base
            prog["r_tip"] = self.r_tip
            self.vao.render(prog, moderngl.TRIANGLES, instances=self.n_lines)

    def get_mesh(self):
        v0s = np.array([[0, 0, 0]], np.float32)
        v1s = np.array([[0, 0, 1]], np.float32)

        # If r_tip is below a certain threshold, we create a proper cone, i.e. with just a single vertex at the top.
        if self.r_tip < 1e-5:
            data = shapes_3d.create_cone_from_to(v0s, v1s, radius=1.0)
        else:
            data = shapes_3d.create_cylinder_from_to(v0s, v1s, radius1=1.0, radius2=1.0)

        return data["vertices"][0], data["faces"]

    @utils_decorators.hooked
    def release(self):
        if self.is_renderable:
            self.vao.release()


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
            kwargs["material"] = kwargs.get("material", Material(color=color, ambient=0.2))
            self.line_colors = kwargs["material"].color
        else:
            assert (
                color.shape[1] == 4 and color.shape[0] == self.n_lines
            ), "Color must be a tuple of 4 values or a numpy array of shape (N_LINES, 4)"
            self.line_colors = color

        super(Lines2D, self).__init__(n_frames=self.lines.shape[0], **kwargs)

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

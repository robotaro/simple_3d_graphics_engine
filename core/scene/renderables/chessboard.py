import numpy as np

from core.scene.node import Node
from core.scene.meshes import Meshes


class Chessboard(Node):
    """A plane that is textured like a chessboard."""

    def __init__(
        self,
        side_length,
        n_tiles,
        color1=(0.0, 0.0, 0.0, 1.0),
        color2=(1.0, 1.0, 1.0, 1.0),
        plane="xz",
        height=0.0,
        tiling=True,
        **kwargs,
    ):
        """
        Initializer.
        :param side_length: Length of one side of the plane.
        :param n_tiles: Number of tiles for the chessboard pattern.
        :param color1: First color of the chessboard pattern.
        :param color2: Second color of the chessboard pattern.
        :param plane: In which plane the chessboard lies. Allowed are 'xz', 'xy', 'yz'.
        :param height: The height of the plane.
        :param kwargs: Remaining kwargs.
        """
        assert plane in ["xz", "xy", "yz"]
        super(Chessboard, self).__init__(**kwargs)
        self.side_length = side_length
        self.n_tiles = n_tiles
        self.c1 = np.array(color1)
        self.c2 = np.array(color2)
        self.plane = plane
        self.height = height
        self.tiling = tiling

        vs, fs, fc, c1_idxs, c2_idxs = self._construct_board()
        self.fcs_tiled = fc
        self.c1_idxs = c1_idxs
        self.c2_idxs = c2_idxs

        self.mesh = Meshes(vs, fs, face_colors=fc)
        self.mesh.backface_culling = False
        self.add(self.mesh, show_in_hierarchy=False)

    # noinspection PyAttributeOutsideInit
    def _construct_board(self):
        """Construct the chessboard mesh."""
        vertices = []
        faces = []
        face_colors = []
        c1_idxs = []  # Store indices into face_colors containing color 1.
        c2_idxs = []  # Store indices into face_colors containing color 2.
        tl = self.side_length / self.n_tiles
        dim1 = "xyz".index(self.plane[0])
        dim2 = "xyz".index(self.plane[1])
        up = "xyz".index("xyz".replace(self.plane[0], "").replace(self.plane[1], ""))

        for r in range(self.n_tiles):
            for c in range(self.n_tiles):
                v0 = np.zeros([3])
                v0[dim1] = r * tl
                v0[dim2] = c * tl

                v1 = np.zeros([3])
                v1[dim1] = (r + 1) * tl
                v1[dim2] = c * tl

                v2 = np.zeros([3])
                v2[dim1] = (r + 1) * tl
                v2[dim2] = (c + 1) * tl

                v3 = np.zeros([3])
                v3[dim1] = r * tl
                v3[dim2] = (c + 1) * tl

                vertices.extend([v0, v1, v2, v3])

                # Need counter-clock-wise ordering
                faces.append([len(vertices) - 4, len(vertices) - 1, len(vertices) - 3])
                faces.append([len(vertices) - 3, len(vertices) - 1, len(vertices) - 2])

                if r % 2 == 0 and c % 2 == 0:
                    c = self.c1
                    fc_idxs = c1_idxs
                elif r % 2 == 0 and c % 2 != 0:
                    c = self.c2
                    fc_idxs = c2_idxs
                elif r % 2 != 0 and c % 2 != 0:
                    c = self.c1
                    fc_idxs = c1_idxs
                else:
                    c = self.c2
                    fc_idxs = c2_idxs
                face_colors.append(c)
                face_colors.append(c)
                fc_idxs.extend([len(face_colors) - 2, len(face_colors) - 1])

        vs = np.stack(vertices)
        vs = vs - np.mean(vertices, axis=0, keepdims=True)
        vs[:, up] = self.height
        fs = np.stack(faces)
        cs = np.stack(face_colors)

        return vs, fs, cs, c1_idxs, c2_idxs

    def _update_colors(self):
        self.fcs_tiled[self.c1_idxs] = self.c1
        self.fcs_tiled[self.c2_idxs] = self.c2 if self.tiling else self.c1
        self.mesh.face_colors = self.fcs_tiled

    def gui(self, imgui):
        u, c1 = imgui.color_edit4("Color 1##color{}'".format(self.unique_name), *self.c1)
        if u:
            self.c1 = c1
            self._update_colors()

        u, c2 = imgui.color_edit4("Color 2##color{}'".format(self.unique_name), *self.c2)
        if u:
            self.c2 = c2
            self._update_colors()

        u, self.tiling = imgui.checkbox("Toggle Tiling", self.tiling)
        if u:
            self._update_colors()

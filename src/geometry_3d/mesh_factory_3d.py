import numpy as np
import trimesh

from src.utilities import utils_mesh_3d
from src.math import mat4

KEY_NAME = "name"
KEY_COLOR = "color"
KEY_RADIUS = "radius"
KEY_LENGTH = "length"
KEY_HEIGHT = "height"
KEY_WIDTH = "width"
KEY_SECTIONS = "sections"
KEY_SEGMENTS = "segments"
KEY_DEPTH = "depth"
KEY_POINT_A = "point_a"
KEY_POINT_B = "point_b"
KEY_TRANSFORM = "transform"

KEY_PRIMITIVE_VERTICES = "vertices"
KEY_PRIMITIVE_NORMALS = "normals"
KEY_PRIMITIVE_UVS = "uvs"
KEY_PRIMITIVE_COLORS = "colors"
KEY_PRIMITIVE_INDICES = "indices"

KEY_SHAPE_CYLINDER = "cylinder"
KEY_SHAPE_BOX = "box"
KEY_SHAPE_CONE = "cone"
KEY_SHAPE_ICOSPHERE = "icosphere"
KEY_SHAPE_CAPSULE = "capsule"

DEFAULT_RADIUS = 0.5
DEFAULT_HEIGHT = 1.0
DEFAULT_COLOR = (1.0, 1.0, 1.0)
DEFAULT_CYLINDER_SECTIONS = 16  # Pie wedges
DEFAULT_CYLINDER_SEGMENTS = 1


class MeshFactory3D:

    """
    This class acts as a factory that generates one single mesh based on a provided list of
    primitives.
    """

    def __init__(self,
                 default_color=DEFAULT_COLOR,
                 use_triangle_normals=True):
        self.default_color = default_color
        self.use_triangle_normals = use_triangle_normals

    def generate_mesh(self, shape_list: list):

        vertices_list = []
        normals_list = []
        colors_list = []
        indices_list = []

        for shape_index, shape in enumerate(shape_list):

            shape_name = shape.get(KEY_NAME, None)
            if shape_name is None:
                raise ValueError(f"[ERROR] Shape does not have a '{KEY_NAME}' field")

            transform_list = shape.get(KEY_TRANSFORM, [])
            transform = np.eye(4, dtype=np.float32) if len(transform_list) == 0 else (
                np.reshape(np.array(transform_list, dtype=np.float32), (4, 4)))

            if shape_name == KEY_SHAPE_CYLINDER:
                vertices, normals, colors, indices = self.create_cylinder(
                    color=shape.get(KEY_COLOR, self.default_color),
                    radius=shape.get(KEY_RADIUS, DEFAULT_RADIUS),
                    sections=shape.get(KEY_SECTIONS, DEFAULT_CYLINDER_SECTIONS),
                    point_a=shape.get(KEY_POINT_A, (0, 0, 0)),
                    point_b=shape.get(KEY_POINT_B, (0, 0, DEFAULT_HEIGHT)),
                    transform=transform)

            elif shape_name == KEY_SHAPE_BOX:
                vertices, normals, colors, indices = self.create_box(
                    width=shape.get(KEY_WIDTH, 1.0),
                    height=shape.get(KEY_HEIGHT, 1.0),
                    depth=shape.get(KEY_DEPTH, 1.0),
                    color=shape.get(KEY_COLOR, self.default_color),
                    transform=transform)

            elif shape_name == KEY_SHAPE_CONE:
                vertices, normals, colors, indices = self.create_cone(
                    height=shape.get(KEY_HEIGHT, DEFAULT_HEIGHT),
                    radius=shape.get(KEY_RADIUS, DEFAULT_RADIUS),
                    sections=shape.get(KEY_SECTIONS, DEFAULT_CYLINDER_SECTIONS),
                    color=shape.get(KEY_COLOR, self.default_color),
                    transform=transform)

            elif shape_name == KEY_SHAPE_ICOSPHERE:
                vertices, normals, colors, indices = self.create_icosphere(
                    radius=shape.get(KEY_RADIUS, DEFAULT_RADIUS),
                    subdivisions=shape.get(KEY_SEGMENTS, 2),
                    color=shape.get(KEY_COLOR, self.default_color),
                    transform=transform)

            elif shape_name == KEY_SHAPE_CAPSULE:
                vertices, normals, colors, indices = self.create_capsule(
                    height=shape.get(KEY_HEIGHT, 2.0),
                    radius=shape.get(KEY_RADIUS, DEFAULT_RADIUS),
                    count=shape.get(KEY_SECTIONS, (8, 8)),
                    color=shape.get(KEY_COLOR, self.default_color),
                    transform=transform)
            else:
                raise Exception(f"[ERROR] Shape '{shape_name}' not supported")

            vertices_list.append(vertices)
            normals_list.append(normals)
            colors_list.append(colors)
            if indices is not None:
                indices_list.append(indices)

        # And Assemble final mesh here
        return {
            KEY_PRIMITIVE_VERTICES: np.concatenate(vertices_list, axis=0),
            KEY_PRIMITIVE_NORMALS: np.concatenate(normals_list, axis=0),
            KEY_PRIMITIVE_COLORS: np.concatenate(colors_list, axis=0),
            KEY_PRIMITIVE_INDICES: np.concatenate(indices_list, axis=0) if len(indices_list) > 0 else None
        }

    def create_cylinder(self,
                        point_a: tuple,
                        point_b: tuple,
                        radius: float,
                        sections: int,
                        color=None,
                        transform=None) -> tuple:

        if color is None:
            color = self.default_color

        if transform is None:
            transform = np.eye(4, dtype=np.float32)

        primitive = trimesh.creation.cylinder(segment=(point_a, point_b),
                                              radius=radius,
                                              sections=sections)

        vertices = np.array(primitive.vertices).astype('f4')
        normals = np.array(primitive.vertex_normals).astype('f4')
        indices = np.array(primitive.faces).astype('i4')
        mat4.mul_vectors3(transform, vertices, vertices)

        if self.use_triangle_normals:
            vertices, normals, _ = utils_mesh_3d.convert_faces_to_triangles(vertices=vertices,
                                                                              uvs=None,
                                                                              faces=indices)
            indices = None

        colors = np.tile(np.array(color, dtype=np.float32), (vertices.shape[0], 1))

        return vertices, normals, colors, indices

    def create_box(self, width: float, height: float, depth: float, color=None, transform=None) -> tuple:
        if color is None:
            color = self.default_color

        if transform is None:
            transform = np.eye(4, dtype=np.float32)

        box = trimesh.creation.box(extents=(width, height, depth))

        vertices = np.array(box.vertices).astype('f4')
        normals = np.array(box.vertex_normals).astype('f4')
        indices = np.array(box.faces).astype('i4')
        mat4.mul_vectors3(transform, vertices, vertices)

        if self.use_triangle_normals:
            vertices, normals, _ = utils_mesh_3d.convert_faces_to_triangles(vertices=vertices,
                                                                            uvs=None,
                                                                            faces=indices)
            indices = None

        colors = np.tile(np.array(color, dtype=np.float32), (vertices.shape[0], 1))

        return vertices, normals, colors, indices

    def create_cone(self, radius: float, height: float, sections: int, color=None, transform=None) -> tuple:
        if color is None:
            color = self.default_color

        if transform is None:
            transform = np.eye(4, dtype=np.float32)

        box = trimesh.creation.cone(radius=radius, height=height, sections=sections)

        vertices = np.array(box.vertices).astype('f4')
        normals = np.array(box.vertex_normals).astype('f4')
        indices = np.array(box.faces).astype('i4')
        mat4.mul_vectors3(transform, vertices, vertices)

        if self.use_triangle_normals:
            vertices, normals, _ = utils_mesh_3d.convert_faces_to_triangles(vertices=vertices,
                                                                            uvs=None,
                                                                            faces=indices)
            indices = None

        colors = np.tile(np.array(color, dtype=np.float32), (vertices.shape[0], 1))

        return vertices, normals, colors, indices

    def create_icosphere(self, radius: float, subdivisions: int, color=None, transform=None) -> tuple:
        if color is None:
            color = self.default_color

        if transform is None:
            transform = np.eye(4, dtype=np.float32)

        icosphere = trimesh.creation.icosphere(radius=radius, subdivisions=subdivisions)

        vertices = np.array(icosphere.vertices).astype('f4')
        normals = np.array(icosphere.vertex_normals).astype('f4')
        indices = np.array(icosphere.faces).astype('i4')
        mat4.mul_vectors3(transform, vertices, vertices)

        if self.use_triangle_normals:
            vertices, normals, _ = utils_mesh_3d.convert_faces_to_triangles(vertices=vertices,
                                                                            uvs=None,
                                                                            faces=indices)
            indices = None

        colors = np.tile(np.array(color, dtype=np.float32), (vertices.shape[0], 1))

        return vertices, normals, colors, indices

    def create_capsule(self, height: float, radius: float, count: tuple, color=None, transform=None) -> tuple:
        if color is None:
            color = self.default_color

        if transform is None:
            transform = np.eye(4, dtype=np.float32)

        capsule = trimesh.creation.capsule(height=height, radius=radius, count=count)

        vertices = np.array(capsule.vertices).astype('f4')
        normals = np.array(capsule.vertex_normals).astype('f4')
        indices = np.array(capsule.faces).astype('i4')
        mat4.mul_vectors3(transform, vertices, vertices)

        if self.use_triangle_normals:
            vertices, normals, _ = utils_mesh_3d.convert_faces_to_triangles(vertices=vertices,
                                                                            uvs=None,
                                                                            faces=indices)
            indices = None

        colors = np.tile(np.array(color, dtype=np.float32), (vertices.shape[0], 1))

        return vertices, normals, colors, indices

    def create_grid_xz(self, num_cells: int, cell_size: float, grid_color=(0.3, 0.3, 0.3)):
        half_size = num_cells * cell_size

        vertices = []
        colors = []

        red_color = (1.0, 0.3, 0.3)
        blue_color = (0.3, 0.3, 1.0)

        # Lines parallel to X axis
        for i in range(2 * num_cells + 1):
            z = -half_size + i * cell_size
            if z == 0:
                # X axis
                vertices.extend([[half_size, 0, z], [-half_size, 0, z]])
                colors.extend([red_color, red_color])
            else:
                vertices.extend([[half_size, 0, z], [-half_size, 0, z]])
                colors.extend([grid_color, grid_color])

        # Lines parallel to Z axis
        for i in range(2 * num_cells + 1):
            x = -half_size + i * cell_size
            if x == 0:
                # Z axis
                vertices.extend([[x, 0, half_size], [x, 0, -half_size]])
                colors.extend([blue_color, blue_color])
            else:
                vertices.extend([[x, 0, half_size], [x, 0, -half_size]])
                colors.extend([grid_color, grid_color])

        vertices = np.array(vertices, dtype=np.float32).reshape(-1, 3)
        colors = np.array(colors, dtype=np.float32).reshape(-1, 3)

        # Create a mesh with lines
        line_indices = np.arange(len(vertices), dtype=np.int32).reshape(-1, 2)
        mesh_data = {
            KEY_PRIMITIVE_VERTICES: vertices,
            KEY_PRIMITIVE_NORMALS: None,
            KEY_PRIMITIVE_COLORS: colors,
            KEY_PRIMITIVE_INDICES: line_indices
        }

        return mesh_data

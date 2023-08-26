import matplotlib.pyplot as plt
import numpy as np

from ecs.math import mat4
from ecs.systems.render_system.font_library import FontLibrary


def font_this():

    font_lib = FontLibrary()
    font_lib.debug_show_texture(font_name="Custom.ttf")
    font_lib.debug_show_texture(font_name="Consolas.ttf")
    font_lib.debug_show_texture(font_name="ProggyClean.ttf")

    window_size = (800, 600)  # width, height

    text_data = font_lib.generate_text_vbo_data(font_name="Consolas.ttf")

    projection_matrix = mat4.orthographic_projection(
        left=-10,
        right=10,
        bottom=-5,
        top=5,
        near=1,
        far=100
    )

    # Calculate points

    # Generate 3D points
    num_points = 10
    points_3d = np.random.rand(num_points, 3) * 20 - 10  # Points in the range [-10, 10]

    # Apply the projection matrix to the points
    points_2d = np.dot(np.hstack((points_3d, np.ones((num_points, 1)))), projection_matrix.T)

    # Extract x and y coordinates of the projected points
    x_coords = points_2d[:, 0]
    y_coords = points_2d[:, 1]

    # Define the window size
    window_size = (8, 8)  # Set the width and height

    # Calculate aspect ratio
    aspect_ratio = window_size[0] / window_size[1]

    # Determine limits based on aspect ratio
    max_range = max(np.abs(x_coords).max(), np.abs(y_coords).max())
    xlim = (-max_range * aspect_ratio, max_range * aspect_ratio)
    ylim = (-max_range, max_range)

    # Create the plot
    plt.figure(figsize=window_size)  # Set the figure size based on window_size
    plt.scatter(x_coords, y_coords, c='b', marker='o')
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.gca().set_aspect('equal', adjustable='box')  # Maintain aspect ratio
    plt.title("Orthographic Projection of 3D Points")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)
    plt.show()


font_this()
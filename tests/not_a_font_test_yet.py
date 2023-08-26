import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


from ecs.math import mat4
from ecs.systems.render_system.font_library import FontLibrary


def font_this():

    font_lib = FontLibrary()
    #font_lib.debug_show_texture(font_name="Custom.ttf")
    font_lib.debug_show_texture(font_name="Consolas.ttf")
    #font_lib.debug_show_texture(font_name="ProggyClean.ttf")

    window_size = (800, 600)  # width, height

    character_data = font_lib.generate_text_vbo_data(font_name="Consolas.ttf", text="Hellow there!", position=(100, 100))

    projection_matrix = mat4.orthographic_projection(
        left=0,
        right=window_size[0],
        bottom=0,
        top=window_size[1],
        near=1,
        far=-1
    )

    # Create the plot with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    ax1.set_xlim(0, window_size[0])
    ax1.set_ylim(0, window_size[1])
    ax1.set_aspect('equal')
    ax1.set_title("Pixel Coordinates")

    ax2.set_xlim(-1, 1)
    ax2.set_ylim(-1, 1)
    ax2.set_aspect('equal')
    ax2.set_title("Projected Coordinates")

    # Calculate initial position
    x_start, y_start = 100, 100

    # Process each character's data
    for char_info in character_data:
        x, y, width, height, u_min, v_min, u_max, v_max, _, horizontal_advance = char_info

        # Plot in the pixel coordinate subplot (ax1)
        rect = Rectangle((x_start + x, y_start + y), width, height, linewidth=1, edgecolor='black', facecolor='none')
        ax1.add_patch(rect)

        # Apply projection and plot in the projected coordinate subplot (ax2)
        char_position = np.array([[x_start + x], [y_start + y], [0], [1]])
        projected_position = np.dot(projection_matrix, char_position)
        projected_rect = Rectangle((projected_position[0], projected_position[1]),
                                   width * projection_matrix[0, 0], height * projection_matrix[1, 1],
                                   linewidth=1, edgecolor='black', facecolor='none')
        ax2.add_patch(projected_rect)

        # Update x position for the next character
        x_start += horizontal_advance

    # Calculate the aspect ratio of the left subplot
    aspect_ratio_left = (ax1.get_ylim()[1] - ax1.get_ylim()[0]) / (ax1.get_xlim()[1] - ax1.get_xlim()[0])

    ax2.set_aspect(aspect_ratio_left)  # Set the aspect ratio of the right subplot to match the left one
    ax2.set_title("Projected Coordinates")

    ax1.set_xlabel("X")
    ax1.set_ylabel("Y")
    ax2.set_xlabel("X (Projected)")
    ax2.set_ylabel("Y (Projected)")

    # Display the plot
    plt.tight_layout()
    plt.show()

font_this()
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from matplotlib import collections as mc
from experimentation.quadrangulation import constants
import numpy as np
from scipy.optimize import linprog

# DEBUG
import matplotlib.pyplot as plt


class PatchSolver:
    
    # =================================================================
    #                       Initialization
    # =================================================================
    
    def __init__(self, ):
        
        # Patch blueprint variables
        self.pattern = -1
        self.p0 = 0
        self.p1 = 0
        self.p2 = 0
        self.p3 = 0
        self.q1 = 0
        self.x = 0
        self.y = 0
        self.inverted = False
        self.rotation = 0
        
        # Initialise patch edge offsets
        self.patch_edge_offset = np.zeros((4,), dtype=np.int32)
        self.patch_edge_size = np.zeros((4,), dtype=np.int32)
        self.macro_edges = {}
        
    # =================================================================
    #                     Incremental Operations
    # =================================================================
    
    def shift_right(self, step_size: int):
        if self.p1 - step_size < 0:
            return
        self.p1 -= step_size
        self.p3 += step_size
        
    def shift_left(self, step_size: int):
        if self.p3 - step_size < 0:
            return
        self.p3 -= step_size
        self.p1 += step_size
        
    def shift_up(self, step_size: int):
        if self.p2 - step_size < 0:
            return
        self.p2 -= step_size
        self.p0 += step_size
        
    def shift_down(self, step_size: int):
        if self.p0 - step_size < 0:
            return
        self.p0 -= step_size
        self.p2 += step_size
        
    def increase_x(self, step_size: int) -> None: ...
    
    def decrease_x(self, step_size: int) -> None: ... 
    
    def increase_y(self, step_size: int) -> None: ...
    
    def decrease_y(self, step_size: int) -> None: ...
    
    def increase_q1(self, step_size: int) -> None: ...
    
    def decrease_q1(self, step_size: int) -> None: ...
    
    # =================================================================
    #                       Core functions
    # =================================================================

    def show_match(self, match: dict):
        """
        Matches are generated from the
        :param match:
        :return:
        """

        subpatch_sizes = self.calculate_subpatch_sizes(match=match)

        self.show_subpatches(subpatch_sizes=subpatch_sizes)

        # TODO: Continue from here

        pass
    
    def calculate_subpatch_sizes(self, match: dict) -> np.ndarray:
        
        """
        This must be executed after the edge vertices have been calculated
        Returns the sides for each of the subpatches around the pattern, and the size of the pattern in the middle
                  
             p3            p1 
           +---+---------+---+
        p2 | 5 |    4    | 3 | p2
           +---+---------+---+
           |   |         |   |
           | 6 |    8    | 2 |
           |   |         |   |
           +---+---------+---+
        p0 | 7 |    0    | 1 | p0
           +---+---------+---+
             p3            p1 

        """

        p0 = match["padding_0"]
        p1 = match["padding_1"]
        p2 = match["padding_2"]
        p3 = match["padding_3"]
        sides = match["transformed_sides"]

        delta_width = p1 + p3
        delta_height = p0 + p2
        
        bottom_width = sides[0] - delta_width
        right_height = sides[1] - delta_height
        top_width = sides[2] - delta_width
        left_height = sides[3] - delta_height
        
        # Update sizes of subpatches
        subpatch_sizes = np.ndarray((9, 4), dtype=np.int32)
        subpatch_sizes[0, :] = (bottom_width, p0, bottom_width, p0)
        subpatch_sizes[1, :] = (p1, p0, p1, p0)
        subpatch_sizes[2, :] = (p1, right_height, p1, right_height)
        subpatch_sizes[3, :] = (p1, self.p2, p1, p2)
        subpatch_sizes[4, :] = (top_width, p2, top_width, p2)
        subpatch_sizes[5, :] = (p3, p2, p3, p2)
        subpatch_sizes[6, :] = (p3, left_height, p3, left_height)
        subpatch_sizes[7, :] = (p3, p0, p3, p0)
        subpatch_sizes[8, :] = (bottom_width, right_height, top_width, left_height)
        
        return subpatch_sizes
   
    def find_all_pattern_matches(self, sides: tuple) -> list:
        """
        Example of sides (16, 5, 5, 4)
            bottom=16,
            right=5,
            top=5,
            left=4

        :param sides: tuple, (4,) number of segments per each side
        :return:
        """
        
        # Solution is only feasible if sum of all sides is an even number
        sum_segments = sides[0] + sides[1] + sides[2] + sides[3]
        if sum_segments % 2 == 1:
            print("[ERROR] Total number of segments ")
            return None

        # Test different rotations and inversions to see which one is solvable
        matches = []
        for (rotation, bottom_index, right_index, top_index, left_index) in constants.SIDES_ORDERED:
            for pattern in range(5):
                parameters = self.solve_pattern_marameters_ilp(
                    pattern=pattern,
                    bottom=sides[bottom_index],
                    right=sides[right_index],
                    top=sides[top_index],
                    left=sides[left_index],
                )
                
                if parameters is None:
                    continue
                
                # Extend patch parameters to contain all necessary info to reconstruct the patch
                parameters["rotation"] = rotation
                parameters["transformed_sides"] = (sides[bottom_index],
                                                   sides[right_index],
                                                   sides[top_index],
                                                   sides[left_index],)
                matches.append(parameters)
                
        return matches

    def solve_pattern_marameters_ilp(self, pattern: int,  bottom: int, right: int, top: int, left: int, method='highs'):
            
        if pattern not in (0, 1, 2, 3, 4):
            raise ValueError(f'[ERROR] Pattern {pattern} not recognized')
            
        # Solve Iterative Linear Programming
        lhs = constants.PATTERNS[pattern]
        rhs = np.array([[bottom], 
                        [right], 
                        [top],
                        [left]], dtype=np.int32)
        rhs += constants.PATTERN_OFFSETS[pattern]
        obj = np.ones((lhs.shape[1], 1), dtype=np.int32)
        ilp_result = linprog(c=obj, A_eq=lhs, b_eq=rhs, method=method)

        if ilp_result.success == False:
            return None
        
        ilp_coeffs = np.rint(ilp_result.x).astype(np.int32)

        # Match pattern
        if pattern == 0:
            return {"pattern": pattern,
                    "padding_0": ilp_coeffs[0],
                    "padding_1": ilp_coeffs[1]}
            
        if pattern == 1:
            return {"pattern": pattern, 
                    "padding_0": ilp_coeffs[0],
                    "padding_1": ilp_coeffs[1],
                    "padding_2": ilp_coeffs[2],
                    "padding_3": ilp_coeffs[3],
                    "x": ilp_coeffs[5]}
            
        if pattern == 2:
            return {"pattern": pattern, 
                    "padding_0": ilp_coeffs[0],
                    "padding_1": ilp_coeffs[1],
                    "padding_2": ilp_coeffs[2],
                    "padding_3": ilp_coeffs[3],
                    "x": ilp_coeffs[5], 
                    "y": ilp_coeffs[6]}
            
        if pattern == 3:
            return {"pattern": pattern, 
                    "padding_0": ilp_coeffs[0],
                    "padding_1": ilp_coeffs[1],
                    "padding_2": ilp_coeffs[2],
                    "padding_3": ilp_coeffs[3],
                    "q1": ilp_coeffs[4], 
                    "x": ilp_coeffs[6]}
            
        if pattern == 4:
            return {"pattern": pattern, 
                    "padding_0": ilp_coeffs[0],
                    "padding_1": ilp_coeffs[1],
                    "padding_2": ilp_coeffs[2],
                    "padding_3": ilp_coeffs[3],
                    "q1": ilp_coeffs[4],
                    "x": ilp_coeffs[6], 
                    "y": ilp_coeffs[7]}
            
        return None
    
    # =================================================================
    #                       Utility Functions
    # =================================================================

    def intersect(self, p1, p2, p3, p4):
        # [Function written by Bing AI]
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4

        # calculate the slope of each line segment
        slope1 = (y2 - y1) / (x2 - x1)
        slope2 = (y4 - y3) / (x4 - x3)

        # calculate the y-intercept of each line segment
        y_intercept1 = y1 - slope1 * x1
        y_intercept2 = y3 - slope2 * x3

        # calculate the x-coordinate of the intersection point
        x_intersect = (y_intercept2 - y_intercept1) / (slope1 - slope2)

        # calculate the y-coordinate of the intersection point
        y_intersect = slope1 * x_intersect + y_intercept1

        return (x_intersect, y_intersect)
    
    def interpolate_2d(self, start: tuple, end: tuple, num_points: int):
        """
        [Code generated by Bing AI]
        
        Generate a series of interpolated points in 2D between two given points.

        :param start: The starting point (x, y) as a tuple of two floats.
        :param end: The ending point (x, y) as a tuple of two floats.
        :param num_points: The number of points to generate as an integer.
        :return: A numpy array of shape (num_points, 2) representing the interpolated points.
        """
        
        x = np.linspace(start[0], end[0], num_points)
        y = np.linspace(start[1], end[1], num_points)
        return np.column_stack((x, y))

    # =================================================================
    #                       DEBUG FUNCTIONS
    # =================================================================

    def show_subpatches(self, subpatch_sizes: np.ndarray, margin=0.02):

        """
        Returns the sides for each of the subpatches around the pattern, and the size of the pattern in the middle

        +---+---------+---+
        | 5 |    4    | 3 |
        +---+---------+---+
        |   |         |   |
        | 6 |    8    | 2 |
        |   |         |   |
        +---+---------+---+
        | 7 |    0    | 1 |
        +---+---------+---+

        """

        x_ticks = np.linspace(start=0, stop=1, num=4, endpoint=True)
        y_ticks = np.linspace(start=0, stop=1, num=4, endpoint=True)

        plot_params = [
            (x_ticks[1], y_ticks[0], x_ticks[2] - x_ticks[1], y_ticks[1] - y_ticks[0]),
            (x_ticks[2], y_ticks[0], x_ticks[3] - x_ticks[2], y_ticks[1] - y_ticks[0]),
            (x_ticks[2], y_ticks[1], x_ticks[3] - x_ticks[2], y_ticks[2] - y_ticks[1]),
            (x_ticks[2], y_ticks[2], x_ticks[3] - x_ticks[2], y_ticks[3] - y_ticks[2]),
            (x_ticks[1], y_ticks[2], x_ticks[2] - x_ticks[1], y_ticks[3] - y_ticks[2]),
            (x_ticks[0], y_ticks[2], x_ticks[1] - x_ticks[0], y_ticks[3] - y_ticks[2]),
            (x_ticks[0], y_ticks[1], x_ticks[1] - x_ticks[0], y_ticks[2] - y_ticks[1]),
            (x_ticks[0], y_ticks[0], x_ticks[1] - x_ticks[0], y_ticks[1] - y_ticks[0]),
            (x_ticks[1], y_ticks[1], x_ticks[2] - x_ticks[1], y_ticks[2] - y_ticks[1]),
        ]

        fig, ax = plt.subplots()
        ax.set_axis_off()

        for index, sides in enumerate(subpatch_sizes):

            if np.sum(subpatch_sizes[index, :] == 0) != 0:
                continue

            bgcolor = None if index != 8 else (0, 1, 0, 0.3)

            self._plot_rectangle_with_sides(
                axis=ax,
                bottom=sides[0],
                right=sides[1],
                top=sides[2],
                left=sides[3],
                x=plot_params[index][0],
                y=plot_params[index][1],
                width=plot_params[index][2],
                height=plot_params[index][3],
                margin=margin,
                bgcolor=bgcolor
            )

        ax.set_aspect('equal')
        plt.show()

    def _plot_rectangle_with_sides(self, axis: plt.Axes, x: float, y: float, width: float, height: float,
                                   margin: float, bottom: int, right: int, top: int, left: int, bgcolor=None):

        """
            +------------------+
            |                  |
        height                 |
            |                  |
           (xy)---- width -----+

        """

        rect = plt.Rectangle((x, y), width, height, fill=True if bgcolor else False, edgecolor='black')
        if bgcolor:
            rect.set_facecolor(bgcolor)
        rect.set_transform(axis.transAxes)
        rect.set_clip_on(False)
        axis.add_patch(rect)

        # Bottom Label
        x_bottom = x + width * 0.5
        y_bottom = y + margin
        axis.text(x_bottom, y_bottom, str(bottom),
                  horizontalalignment='center',
                  verticalalignment='bottom',
                  transform=axis.transAxes)

        # Right Label
        x_right = x + width - margin
        y_right = y + height * 0.5
        axis.text(x_right, y_right, str(right),
                  horizontalalignment='right',
                  verticalalignment='center',
                  transform=axis.transAxes)

        # Top Label
        x_top = x + width * 0.5
        y_top = y + height - margin
        axis.text(x_top, y_top, str(top),
                  horizontalalignment='center',
                  verticalalignment='top',
                  transform=axis.transAxes)

        # Left Label
        x_left = x + margin
        y_left = y + height * 0.5
        axis.text(x_left, y_left, str(left),
                  horizontalalignment='left',
                  verticalalignment='center',
                  transform=axis.transAxes)

    def draw_regular_grid(self, corners: list, u: int, v: int, edge_color: tuple, edge_width=2, fill_color=None):
        """_summary_

        Parameters
        ----------
        corners : list of tuples
            List [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
            Points follow order [SW, SE, NE, NW]
        u : int
            number of U divisions
        v : int
            number of V divisions
        edge_color : tuple
            RGB color of the grid edges
        edge_width : float
            Thickness of the grid's edges
        fill_color : tuple
            RGB color filling all mesh cells
        """

        BOTTOM = 0
        RIGHT = 1
        TOP = 2
        LEFT = 3

        OPPOSITE_SIDE_MAP = {
            BOTTOM: TOP,
            RIGHT: LEFT,
            TOP: BOTTOM,
            LEFT: RIGHT
        }

        n_sides_order = [u, v, u, v]
        side_points = []

        fig, ax = plt.subplots(figsize=(5, 5), dpi=150)

        # Convert corners to a numpy array for easier manipulation
        corners_np = np.array(corners, dtype=np.float32)

        # Calculate point interpolations
        for edge_index, n_sides in enumerate(n_sides_order):
            a = edge_index
            b = (edge_index + 1) % len(corners)
            points = np.ndarray((n_sides, 2), dtype=np.float32)
            points[:, 0] = np.linspace(start=corners_np[a, 0], stop=corners_np[b, 0], num=n_sides, endpoint=True)
            points[:, 1] = np.linspace(start=corners_np[a, 1], stop=corners_np[b, 1], num=n_sides, endpoint=True)
            side_points.append(points)

        # Build line segments to be drawn
        line_segments = []
        for side_index, points_a in enumerate(side_points):
            points_b = side_points[OPPOSITE_SIDE_MAP[side_index]]
            num_points = points_a.shape[0]
            for index_a in range(num_points):
                index_b = num_points - index_a - 1
                line_segments.append([(points_a[index_a, 0], points_a[index_a, 1]),
                                      (points_b[index_b, 0], points_b[index_b, 1])])

        # Draw filling color, if specified
        if fill_color is not None:
            ax.fill(corners_np[:, 0], corners_np[:, 1], facecolor=fill_color)

        # Draw all line segments
        lc = mc.LineCollection(line_segments, color=(*edge_color, 1), linewidths=edge_width)
        ax.add_collection(lc)

        ax.set_aspect('equal')
        plt.show()


# =================================================================
#                              DEMO
# =================================================================


def demo():

    patch = PatchSolver()

    corners = [(0, 0),
               (0.5, 0),
               (1, 0.75),
               (0.5, 1)]

    patch.draw_regular_grid(
        corners=corners,
        u=5,
        v=4,
        edge_color=(1, 1, 1),
        fill_color="tab:blue")

    return

    list_of_sides = [
        (16, 5, 5, 4),
        (5, 5, 4, 16),
        (5, 4, 16, 5),
        (4, 16, 5, 5),
        (5, 4, 5, 16),
        (12, 7, 5, 2),
        (5, 3, 7, 5),
        (14, 17, 1, 20),
        (8, 2, 1, 1),
        (5, 1, 1, 1),
    ]

    for sides in list_of_sides:
        matches = patch.find_all_pattern_matches(sides=sides)

        for match in matches:
            patch.show_match(match=match)

if __name__ == "__main__":
    demo()
    

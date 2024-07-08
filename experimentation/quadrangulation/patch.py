import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from re import sub
from experimentation.quadrangulation import constants
import numpy as np
from scipy.optimize import linprog
from typing import Tuple

# DEBUG
import matplotlib.pyplot as plt
MARGIN = 0.1
MAX_NUM_VERTICES = 625


class QuadEdge:
    
    def __init__(self) -> None:
        self.neighbor_quad_index = -1
        self.vertex_indices = []


class UniformQuad:
    
    def __init__(self) -> None:
        self.bottom = QuadEdge()
        self.right = QuadEdge()
        self.top = QuadEdge()
        self.left = QuadEdge()


class Patch:
    
    __slots__ = ['bottom',
                 'right',
                 'top',
                 'left',
                 'num_sides',
                 'patch_edge_offset',
                 'patch_edge_size',
                 'pattern',
                 'p0',
                 'p1',
                 'p2',
                 'p3',
                 'q1',
                 'x',
                 'y',
                 'inverted', 'rotation', 'subpatch_sizes', 'subpatch_edge_indices',
                 'num_vertices', 'vertices', 'macro_edges']
    
    # =================================================================
    #                       Initialization
    # =================================================================
    
    def __init__(self, patch_corners: np.ndarray, bottom: int, right: int, top: int, left: int):
        
        # Number of sides for each corner
        self.bottom = bottom
        self.right = right
        self.top = top
        self.left = left
        self.num_sides = (bottom, right, top, left)
        
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
        
        # Subpatch variables
        self.subpatch_sizes = np.zeros((9, 1), dtype=np.int32)
        self.subpatch_edge_indices = [{'bottom': None, 'right': None, 'top': None, 'left': None} for _ in range(9)]
        
        # Initialize vertices and copy 4 corner vertices in their respective locations
        self.vertices = np.zeros((MAX_NUM_VERTICES, 2), dtype=np.float32)
        self.vertices[:4 , :] = patch_corners
        self.num_vertices = 4
        
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
    
    def process(self) -> None:
        
        # Stage 1) Find all patterns that match the patch number of sides
        matches = self.find_all_pattern_matches(
            bottom=self.bottom,
            right=self.right,
            top=self.top,
            left=self.left
        )
        # TEMPORARY: Assume there is only one match for now
        pattern_match = matches[0]
        
        subpatch_sizes = self.calculate_subpatch_sizes(pattern=pattern_match)
        
        patch_perimeter_subpatches = self.generate_patch_perimeter_from_subpatches(subpatch_sizes=subpatch_sizes)
        
        self.calculate_patch_main_vertices(subpatch_sizes=subpatch_sizes)

        valid_subpatche_indices = self.get_valid_subpatche_indices(subpatch_sizes)
        
        self.generate_valid_subpatch_edges(subpatch_sizes=subpatch_sizes, 
                                           valid_subpatch_indices=valid_subpatche_indices)
        
        self.calculate_pattern_main_vertices()
        
        
        # [ DEBUG ]
        fig, ax = plt.subplots()
        ax.scatter(self.vertices[0:16, 0], self.vertices[0:16, 1], alpha=0.5)
        ax.grid(True)
        ax.set_aspect('equal')
        plt.show()
    
    def calculate_subpatch_sizes(self, pattern: dict) -> None:
        
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
        
        delta_width = pattern['p1'] + pattern['p3']
        delta_height = pattern['p0'] + pattern['p2']    
        
        bottom_width = self.bottom - delta_width
        right_height = self.right - delta_height
        top_width = self.top - delta_width
        left_height = self.left - delta_height
        
        # Update sizes of subpatches
        subpatch_sizes = np.ndarray((9, 4), dtype=np.int32)
        subpatch_sizes[0, :] = (bottom_width, pattern['p0'], bottom_width, pattern['p0'])
        subpatch_sizes[1, :] = (pattern['p1'], pattern['p0'], pattern['p1'], pattern['p0'])
        subpatch_sizes[2, :] = (pattern['p1'], right_height, pattern['p1'], right_height)
        subpatch_sizes[3, :] = (pattern['p1'], self.p2, pattern['p1'], pattern['p2'])
        subpatch_sizes[4, :] = (top_width, pattern['p2'], top_width, pattern['p2'])
        subpatch_sizes[5, :] = (pattern['p3'], pattern['p2'], pattern['p3'], pattern['p2'])
        subpatch_sizes[6, :] = (pattern['p3'], left_height, pattern['p3'], left_height)
        subpatch_sizes[7, :] = (pattern['p3'], pattern['p0'], pattern['p3'], pattern['p0'])
        subpatch_sizes[8, :] = (bottom_width, right_height, top_width, left_height)
        
        return subpatch_sizes

    def calculate_patch_main_vertices(self, subpatch_sizes: np.ndarray) -> None:
        
        for edge_label, indices in constants.PATCH_PERIMETER_EDGES_BY_CORNERS.items():
            ca, cb = indices['patch_corners']
            va, vb = indices['patch_vertices']
            side_sizes = subpatch_sizes[indices['subpatches'], :][:, indices['subpatch_array_column']].flatten()
            out_a, out_b = self.interpolate_two_patch_perimeter_vertices(
                corner_a=self.vertices[ca, :],
                corner_b=self.vertices[cb, :],
                num_sides_a_to_b=side_sizes
            )
            self.vertices[va, :], self.vertices[vb, :] = out_a, out_b
            self.num_vertices += 2
        
        for out_index, edge_indices in constants.SUBPATCH_INNER_CORNERS_EDGE_INTERSECTIONS.items():
            new_vertex = self.intersect(
                p1=self.vertices[edge_indices[0][0]],
                p2=self.vertices[edge_indices[0][1]],
                p3=self.vertices[edge_indices[1][0]],
                p4=self.vertices[edge_indices[1][1]],
            )
            self.vertices[out_index, :] = new_vertex
            self.num_vertices += 1

    def generate_patch_perimeter_from_subpatches(self, subpatch_sizes: np.ndarray) -> dict:
        valid_subpatch_mask = np.sum(subpatch_sizes == 0, axis=1) == 0
        top_left_subindex = np.argwhere(valid_subpatch_mask[constants.SUBPATCH_TOP_LEFT_INDEX_SEQUENCE])[0, 0]
        top_left_index = int(constants.SUBPATCH_TOP_LEFT_INDEX_SEQUENCE[top_left_subindex])
        bottom_right_subindex = np.argwhere(valid_subpatch_mask[constants.SUBPATCH_BOTTOM_RIGHT_INDEX_SEQUENCE])[0, 0]
        bottom_right_index = int(constants.SUBPATCH_BOTTOM_RIGHT_INDEX_SEQUENCE[bottom_right_subindex])
        return constants.SUBPATCH_TL_AND_BR_MAP[(top_left_index, bottom_right_index)]
    
    def get_valid_subpatche_indices(self, subpatch_sizes: np.ndarray) -> list:
        return np.argwhere(np.sum(subpatch_sizes == 0, axis=1) == 0).flatten()
    
    def generate_valid_subpatch_edges(self, subpatch_sizes: np.ndarray, valid_subpatch_indices: list) -> None:
        
        for subpatch_index in valid_subpatch_indices:
            
            corner_vertices = constants.SUBPATCH_CORNER_INDICES[subpatch_index]
            for corner_index, vertex_index in enumerate(corner_vertices):
                
                next_corner_index = (corner_index + 1) % 4
                next_vertex_index = corner_vertices[next_corner_index]
                vertex_a = self.vertices[vertex_index, :]
                vertex_b = self.vertices[next_vertex_index, :]
                edge_key = (vertex_index, next_vertex_index)
                reverse_edge_key = (next_vertex_index, vertex_index)
                
                if edge_key in self.macro_edges:
                    g = 0
                    continue
                
                if reverse_edge_key in self.macro_edges:
                    # TODO: Check if flip really returns a reference of the reversed array
                    self.macro_edges[edge_key] = np.flipud(self.macro_edges[reverse_edge_key])
                    continue
                
                num_vertices = subpatch_sizes[subpatch_index, corner_index]
                self.macro_edges[edge_key] = self.interpolate_2d(start=vertex_a, end=vertex_b, num_points=num_vertices)

    def calculate_pattern_main_vertices(self) -> dict:
        pass
   
    def find_all_pattern_matches(self, bottom: int, right: int, top: int, left: int) -> list:
        
        # Solution is only feasible if sum of all sides is an even number
        sum_sides = top + right + bottom + left
        if sum_sides % 2 == 1:
            return None
        
        quad_sides = (bottom, right, top, left)
        
        # Test different rotations and inversions to see which one is solvable
        matches = []
        for (rotation, inverted, b_index, r_index, t_index, l_index) in constants.SIDES_ORDERED:
            for pattern in range(5):
                parameters = self.solve_pattern_marameters_ilp(
                    pattern=pattern,
                    bottom=quad_sides[b_index],
                    right=quad_sides[r_index],
                    top=quad_sides[t_index],
                    left=quad_sides[l_index],
                )
                
                if parameters is None:
                    continue
                
                # Extend patch parameters to contain all necessary info to reconstruct the patch
                parameters["inverted"] = inverted
                parameters["rotation"] = rotation
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
                    "p0": ilp_coeffs[0], 
                    "p1": ilp_coeffs[1]}
            
        if pattern == 1:
            return {"pattern": pattern, 
                    "p0": ilp_coeffs[0], 
                    "p1": ilp_coeffs[1], 
                    "p2": ilp_coeffs[2], 
                    "p3": ilp_coeffs[3], 
                    "x": ilp_coeffs[5]}
            
        if pattern == 2:
            return {"pattern": pattern, 
                    "p0": ilp_coeffs[0], 
                    "p1": ilp_coeffs[1], 
                    "p2": ilp_coeffs[2], 
                    "p3": ilp_coeffs[3], 
                    "x": ilp_coeffs[5], 
                    "y": ilp_coeffs[6]}
            
        if pattern == 3:
            return {"pattern": pattern, 
                    "p0": ilp_coeffs[0], 
                    "p1": ilp_coeffs[1], 
                    "p2": ilp_coeffs[2], 
                    "p3": ilp_coeffs[3],
                    "q1": ilp_coeffs[4], 
                    "x": ilp_coeffs[6]}
            
        if pattern == 4:
            return {"pattern": pattern, 
                    "p0": ilp_coeffs[0], 
                    "p1": ilp_coeffs[1], 
                    "p2": ilp_coeffs[2], 
                    "p3": ilp_coeffs[3],
                    "q1": ilp_coeffs[4],
                    "x": ilp_coeffs[6], 
                    "y": ilp_coeffs[7]}
            
        return None
                
    def tesselate_pattern(self):
        pass
    
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
    
    def interpolate_two_patch_perimeter_vertices(self,
                                                 corner_a: np.array, 
                                                 corner_b: np.array, 
                                                 num_sides_a_to_b: tuple) -> tuple:
        """
        This function takes the sides of three subpatches that make up one
        edge of the patche's perimeter and return the two vertices in between
        them.

        Parameters
        ----------
        points_a : np.array
            2D location of the 
        points_b : np.array
            _description_
        num_sides_a_to_b : tuple
            list of sizes of the three sides that make up the entire length
            of the edge from corner_a to corner_b

        Returns
        -------
        np.ndarray
            location of the two interpolated points
        """
        
        inv_total_num_sides = 1.0 / np.sum(num_sides_a_to_b)
        diff_vector = corner_b - corner_a
        unit_vector = diff_vector / np.linalg.norm(diff_vector)
        subvertex_a = unit_vector * num_sides_a_to_b[0] * inv_total_num_sides + corner_a
        subvertex_b = unit_vector * num_sides_a_to_b[1] * inv_total_num_sides + subvertex_a
        
        return subvertex_a, subvertex_b
        

    # =================================================================
    #                       DEBUG FUNCTIONS
    # =================================================================
    
    def _plot_rectangle_with_sides(self, axis: plt.Axes, x: float, y: float, width: float, height: float, 
                                   margin: float, bottom: int, right: int, top: int, left: int):
    
        """
            +------------------+
            |                  |
        height                 |
            |                  |
           (xy)---- width -----+
        
        """

        rect = plt.Rectangle((x, y), width, height, fill=False)
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

    def show_subpatches(self, margin=0.02):
        
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

        # TODO: Determine if this is executed every time
        self.calculate_subpatch_sizes()
        
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
        
        for index, sides in enumerate(self.subpatch_sizes):
            print(index)
            
            if np.sum(self.subpatch_sizes[index, :] == 0) != 0:
                continue

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
                margin=margin
            )
    
        ax.set_aspect('equal')
        plt.show()

# =================================================================
#                              DEMO
# =================================================================

def demo():
  
    corners = np.array([(0, 0),
                        (1, 0),
                        (1, 1),
                        (0, 1)], 
                        dtype=np.float32)

    patch = Patch(
        patch_corners=corners,
        bottom=16,
        right=5,
        top=5,
    left=4)

    patch.process()

    #patch.shift_right(step_size=2)
    #patch.shift_down(step_size=1)

    patch.show_subpatches()


if __name__ == "__main__":
    
    
    demo()
    

"""
    def generate_patch_edge_vertices(self) -> None:
        
        # Corner vertices have already been places in the __init__ function!
        
        # Place patch edge vertices in-between edge vertices
        
        index_a = self.num_vertices
        for i in range(4):
            i_next = (i + 1) % 4
            num_vertices = self.num_sides[i] + 1
            
            # First and last vertices are the already-defined corner vertices
            if num_vertices <= 2:
                self.patch_edge_offset[i] = -1
                self.patch_edge_size[i] = 0
                continue
            
            num_new_vertices = num_vertices - 2
            index_b = index_a + num_new_vertices
            
            # Calculate interpolated vertices for the outer edge
            self.vertices[index_a: index_b, :] = self.interpolate_2d(
                start=self.vertices[i, :], 
                end=self.vertices[i_next, :], 
                num_points=num_vertices
                )[1:-1, :]
            
            # Update their offsets
            self.patch_edge_offset[i] = index_a
            self.patch_edge_size[i] = num_new_vertices
            index_a += num_new_vertices
"""
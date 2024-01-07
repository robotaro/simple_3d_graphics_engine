import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import numpy as np
from typing import List, Tuple
from playground.new_quadrangulation import constants

# [DEBUG]
import matplotlib.pyplot as plt

# Check quadrilateral projections: https://www.particleincell.com/2012/quad-interpolation/

class Subpatch:
    
    def __init__(self, rows: int, cols: int) -> None:
        self.vertices = np.ndarray((rows, cols, 2), dtype=np.float32)
        self.connections = np.ndarray((rows, cols, 2), dtype=np.float32)

    def connect_subpatch() -> None:
        
        pass

MAX_NUM_VERTICES = 1000
MAX_NUM_EDGES = 250
MAX_NUM_QUADS = 75

class Quad:
    
    def __init__(self, rows: int, cols: int) -> None:
        self.global_indices = np.ones((rows, cols), dtype=np.int32) * -1
        x = np.linspace(0, 1, cols, endpoint=True)
        y = np.linspace(0, 1, rows, endpoint=True)
        xv, yv = np.meshgrid(x, y)
        self.grid = np.dstack((xv, yv))
        self.grid_flat = np.reshape(self.grid, (-1, 2))
        self.vertices = None
    
    def connect_to():
        pass
    
    def generate_grid(self, corners: np.ndarray) -> np.ndarray:
        
        def bilinear_interpolation(p, q00, q10, q01, q11):
            x, y = p
            x_floor, y_floor = int(x), int(y)
            q_floor = q00 + (q10 - q00) * (x - x_floor)
            q_ceil = q01 + (q11 - q01) * (x - x_floor)
            return q_floor + (q_ceil - q_floor) * (y - y_floor)

        inv_quad = np.linalg.inv(np.array([
            [corners[0][0], corners[1][0], corners[2][0]],
            [corners[0][1], corners[1][1], corners[2][1]],
            [1, 1, 1]
        ]))
        
        result = np.zeros_like(self.grid_flat)
        for i, point in enumerate(self.grid_flat):
            homog_point = np.array([point[0], point[1], 1])
            homog_transformed = inv_quad @ homog_point
            transformed = homog_transformed[:2] / homog_transformed[2]
            result[i] = bilinear_interpolation(transformed, corners[0], corners[1], corners[3], corners[2])
            
        self.vertices = result

class QuadNetwork:
    
    def __init__(self) -> None:
        
        """
        vertex = (x, y, edge_index, value_along_edge)
        edge = (vertex_index_a, vertex_index_b, num_segments, quad_index_a, quad_index_b)  # Add which part
        quad = (edge_index_top, edge_index_right, edge_index_bottom, edge_index_left)
        
        """
        
        self.vertices = np.empty((MAX_NUM_VERTICES, 2), dtype=np.float32)
        self.edges = {}
        self.quads = []
        self.num_vertices = 0
        
    def get_vertex(self, vertex_index: int) -> tuple:
        return float(self.vertices[vertex_index, 0]), float(self.vertices[vertex_index, 1])
        
    def add_vertex(self, x=0.0, y=0.0, edge_index=-1, edge_location=-1.0) -> int:
        self.vertices.append((x, y, edge_index, edge_location))
        return len(self.vertices) - 1
    
    def create_edge(self, edge_key: tuple, num_sides=1) -> int:
        
        in_between_vertices = None
        if num_sides > 1:
            first = edge_key[0]
            last = edge_key[1]
            index_a = self.num_vertices
            index_b = index_a + num_sides
            x = np.linspace(start=self.vertices[first, 0], stop=self.vertices[last, 0], num=num_sides+1, endpoint=True)
            y = np.linspace(start=self.vertices[first, 1], stop=self.vertices[last, 1], num=num_sides+1, endpoint=True)
            self.vertices[np.hstack((x, y))]
            in_between_vertices = np.arange(start=index_a, stop=index_b, )
            
        
        self.edges[edge_key] = {
            "in_between_vertices": in_between_vertices
        }
        return len(self.edges) - 1
    
    
    def add_quad(self, top_edge: int, right_edge: int, bottom_edge: int, left_edge: int) -> int:
        self.quads.append(top_edge, right_edge, bottom_edge, left_edge)
        return len(self.quads) - 1
    

if __name__ == "__main__":
    
    
    #bard_ai_code()
    
    corners = np.array(
        [[0.25, 0.25],
         [0.8, 0.3],
         [0.7, 0.9],
         [0.15, 0.85]])
    
    q0 = Quad(rows=6, cols=3)
    q0.generate_grid(corners=corners)
    
    plt.scatter(q0.grid_flat[:, 1], q0.grid_flat[:, 0])
    plt.scatter(q0.vertices[:, 1], q0.vertices[:, 0])
    plt.show()
    
    network = QuadNetwork()
    
    c0 = network.add_vertex(x=0.0, y=0.0)
    c1 = network.add_vertex(x=1.0, y=0.0)
    c2 = network.add_vertex(x=1.0, y=.0)
    c3 = network.add_vertex(x=0.0, y=1.0)
    
    edge_c0c1 = network.create_edge(edge_key=(c0, c1), num_sides=8)
    edge_c1c2 = network.add_edge(edge_points=(c1, c2), num_sides=6)
    edge_c2c3 = network.add_edge(edge_points=(c2, c3), num_sides=4)
    edge_c3c0 = network.add_edge(edge_points=(c3, c0), num_sides=4)
    
    v0 = network.add_vertex(edge_index=edge_c0c1, edge_location=0.25)
    v1 = network.add_vertex(edge_index=edge_c0c1, edge_location=0.5)
    v2 = network.add_vertex(edge_index=edge_c0c1, edge_location=0.75)
    v3 = network.add_vertex(edge_index=edge_c1c2, edge_location=0.5)
 
    v4 = network.add_vertex(x=0.75, y=0.25)
    
    
    
    
    g = 0
    
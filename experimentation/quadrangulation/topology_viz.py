import matplotlib.pyplot as plt
from matplotlib import collections as mc
import numpy as np

class TopoViz:
    
    """
            0
        +-------+
        |       |
      3 |       |  1
        +-------+
            2
    """
    
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3
    
    OPPOSITE_SIDE_MAP = {
        TOP: BOTTOM,
        RIGHT: LEFT,
        BOTTOM: TOP,
        LEFT: RIGHT
    }
    
    def __init__(self, xlim=(0, 1), ylim=(0, 1), fig_size=(6, 4), dpi=100) -> None:
        self.xlim = xlim
        self.ylim = ylim
        self.side_lims = [self.ylim, self.xlim, self.ylim, self.xlim]
        self.fig, self.ax = plt.subplots(figsize=fig_size, dpi=dpi)
        self.ax.set(xlim=self.xlim, ylim=self.ylim, xticks=[], yticks=[])

        
    def extract_regular_meshes(self, quad_sides: tuple) -> tuple:

        # First Cut: Horizontal 
        common_min = np.minimum(quad_sides[1] - 1, quad_sides[3] - 1)
        irregular_mesh_top = (quad_sides[TopoViz.TOP], 
                              quad_sides[TopoViz.RIGHT] - common_min, 
                              quad_sides[TopoViz.BOTTOM], 
                              quad_sides[TopoViz.LEFT] - common_min)
        regular_mesh_bottom = (quad_sides[TopoViz.BOTTOM], 
                               common_min, 
                               quad_sides[TopoViz.BOTTOM], 
                               common_min)

        # Second Cut: vertical
        common_min = np.minimum(irregular_mesh_top[0] - 1, irregular_mesh_top[2] - 1)
        irregular_mesh_top_left = (irregular_mesh_top[0] - common_min, 
                                   irregular_mesh_top[1] , 
                                   irregular_mesh_top[2] - common_min, 
                                   irregular_mesh_top[3])
        regular_mesh_top_right = (common_min, 
                                 irregular_mesh_top_left[1], 
                                 common_min, 
                                 irregular_mesh_top_left[1])
        
        return regular_mesh_bottom, regular_mesh_top_right, irregular_mesh_top_left
        
    def draw_regular_grid(self, corners: np.ndarray, u: int, v: int, edge_color: tuple, edge_width=2, fill_color=None):
        
        """_summary_

        Parameters
        ----------
        corners : Numpy ndarray <float32>
            Array (4, 2) <float32>
            Rows follow order [NW, NE, SE, SW]
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
        n_sides_order = [u, v, u, v]
        side_points = []
        
        # Calculate point interpolations
        for edge_index, n_sides in enumerate(n_sides_order):
            a = edge_index
            b = (edge_index + 1) % corners.shape[0]
            points = np.ndarray((n_sides, 2), dtype=np.float32)
            points[:, 0] = np.linspace(start=corners[a, 0], stop=corners[b, 0], num=n_sides, endpoint=True)
            points[:, 1] = np.linspace(start=corners[a, 1], stop=corners[b, 1], num=n_sides, endpoint=True)
            side_points.append(points)
            
        # Build line segments to be drawn
        line_segments = []
        for side_index, points_a in enumerate(side_points):
            
            points_b = side_points[TopoViz.OPPOSITE_SIDE_MAP[side_index]]
            num_points = points_a.shape[0]
            for index_a in range(num_points):
                index_b = num_points - index_a - 1
                line_segments.append([(points_a[index_a, 0], points_a[index_a, 1]), 
                                      (points_b[index_b, 0], points_b[index_b, 1])])

        # Draw filling color, if specified
        if fill_color is not None:
            self.ax.fill(corners[:, 0], corners[:, 1], facecolor=fill_color)

        # Draw all line segments
        lc = mc.LineCollection(line_segments, color=(*edge_color, 1), linewidths=edge_width)
        self.ax.add_collection(lc)
        
    def show(self, quad_sides: tuple):
        
        # (top, right, down, left)
        
        # Calculate ticks
        side_ticks = list()
        for index in range(len(quad_sides)):
            side_ticks.append(np.linspace(start=0, stop=1, num=quad_sides[index] + 1, endpoint=True))

        # Plot quad ticks
        #self.ax.plot(side_ticks[0], [1 for _ in range(len(side_ticks[0]))], 'o')   # Top
        #self.ax.plot([1 for _ in range(len(side_ticks[1]))], side_ticks[1], 'o')   # Right 
        #self.ax.plot(side_ticks[2], [0 for _ in range(len(side_ticks[2]))], 'o')  # Bottom
        #self.ax.plot([0 for _ in range(len(side_ticks[3]))], side_ticks[3], 'o')  #Left
        
        # Interpolate initial quad_sides
        quad_ticks = []
        for index in range(len(quad_sides)):
            quad_ticks.append(
                np.linspace(start=self.side_lims[index][0], 
                            stop=self.side_lims[index][1], 
                            num=quad_sides[index], 
                            endpoint=True))
        
        
        regular_bottom, regular_top_right, irregular_top_left = self.extract_regular_meshes(quad_sides=quad_sides)
        
        regular_bottom_corners = [(self.xlim[0], quad_ticks[3][regular_bottom[0] - 1]),  # NW
                                  (self.xlim[1], quad_ticks[1][regular_bottom[1] - 1]),  # NE
                                  (self.xlim[1], self.ylim[0]),  # SE
                                  (self.xlim[0], self.ylim[0]),  # SW
                                  ]
        regular_bottom_corners = np.array(regular_bottom_corners, dtype=np.float32)
        
        #corners = np.array([(0, 0), (0.5, 0), (1, 0.75), (0, 1)], dtype=np.float32)
        self.draw_regular_grid(
            corners=regular_bottom_corners, 
            u=regular_bottom[0],
            v=regular_bottom[1], 
            edge_color=(1, 1, 1), fill_color="tab:blue")

        y = [0.22, 0.34, 0.5, 0.56, 0.78]
        x = [0.17, 0.5, 0.855]
        X, Y = np.meshgrid(x, y)

        self.ax.set_aspect('equal')
        plt.show()

def main():
    
    viz = TopoViz()
    quad_sides = (4, 16, 5, 5)
    viz.show(quad_sides=quad_sides)
    
if __name__ == "__main__":

    main()
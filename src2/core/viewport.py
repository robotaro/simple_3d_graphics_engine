

class Viewport:

    def __init__(self, params: dict):
        self.viewport_screen_ratio = params.get("viewport_screen_ratio", (0.0, 0.0, 1.0, 1.0))
        self.viewport_pixels = None
        self.camera = None

    def is_inside_viewport(self, screen_gl_position: tuple) -> bool:
        if self.viewport_pixels is None:
            return False

        flag_x = self.viewport_pixels[0] <= screen_gl_position[0] < (self.viewport_pixels[2] + self.viewport_pixels[0])
        flag_y = self.viewport_pixels[1] <= screen_gl_position[1] < (self.viewport_pixels[3] + self.viewport_pixels[1])

        return flag_x & flag_y

    def update_size(self, parent_width_pixels: int, parent_height_pixels: int):
        self.viewport_pixels = (int(self.viewport_screen_ratio[0] * parent_width_pixels),
                                int(self.viewport_screen_ratio[1] * parent_height_pixels),
                                int(self.viewport_screen_ratio[2] * parent_width_pixels),
                                int(self.viewport_screen_ratio[3] * parent_height_pixels))

        if self.camera:
            self.camera.update_projection_matrix(viewport_pixels=self.viewport_pixels)

from typing import Optional, Tuple


class Viewport:

    __slots__ = [
        "rect_ratio",
        "rect_pixels",
        "camera"
    ]

    def __init__(self, rect_ratio: Optional[Tuple] = None):
        self.rect_ratio = rect_ratio if rect_ratio is not None else (0.0, 0.0, 1.0, 1.0)
        self.rect_pixels = None
        self.camera = None

    def is_inside_viewport(self, screen_gl_position: tuple) -> bool:
        if self.rect_pixels is None:
            return False

        flag_x = self.rect_pixels[0] <= screen_gl_position[0] < (self.rect_pixels[2] + self.rect_pixels[0])
        flag_y = self.rect_pixels[1] <= screen_gl_position[1] < (self.rect_pixels[3] + self.rect_pixels[1])

        return flag_x & flag_y

    def update_size(self, container_size_pixels: tuple) -> None:

        """

        :param container_size_pixels: tuple, (width, height) <int, int>
        :return:
        """
        self.rect_pixels = (int(self.rect_ratio[0] * container_size_pixels[0]),
                            int(self.rect_ratio[1] * container_size_pixels[1]),
                            int(self.rect_ratio[2] * container_size_pixels[0]),
                            int(self.rect_ratio[3] * container_size_pixels[1]))

        if self.camera:
            self.camera.update_projection_matrix(viewport_pixels=self.rect_pixels)

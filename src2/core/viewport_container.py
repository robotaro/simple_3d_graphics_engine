from src2.core.viewport import Viewport


class ViewportContainer:
    __slots__ = [
        "rect_pixels",
        "viewports"
    ]

    def __init__(self, rect_pixels: tuple):
        self.rect_pixels = rect_pixels
        self.viewports = {}

    def add_viewport(self, name: str, viewport: Viewport):
        if name in self.viewports:
            raise KeyError(f"[ERROR] Viewport key '{name}' already exists")
        self.viewports[name] = viewport
        self._update_single_viewport(viewport=viewport)

    def update(self, new_rect_pixels: int):
        self.rect_pixels = new_rect_pixels
        for _, viewport in self.viewports.items():
            self._update_single_viewport(viewport=viewport)

    def _update_single_viewport(self, viewport):
        width_pixels = self.rect_pixels[2] - self.rect_pixels[0]
        height_pixels = self.rect_pixels[3] - self.rect_pixels[1]
        viewport.update_size(parent_width_pixels=width_pixels,
                             parent_height_pixels=height_pixels)

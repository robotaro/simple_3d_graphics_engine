

class Viewport:

    __slots__ = ["camera", "x", "y", "width", "height"]

    def __init__(self, x: int, y: int, width: int, height: int):

        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def contains(self, x: int, y: int) -> bool:
        """
        Check if point is contained inside this viewport
        :param x: int, X screen coordinate
        :param y: int, Y screen coordinate
        :return:
        """
        return x >= self.x and x < (self.x + self.width) and y >= self.y and y < (self.y + self.height)

    def to_tuple(self) -> tuple:
        return (self.x, self.y, self.width, self.height)
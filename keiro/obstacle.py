from vector2d import Vec2d
from particle import Obstacle as ObstacleBase


class Obstacle(object):
    def __init__(self):
        self.bounds = []

    def render(self, screen):
        for line in self.bounds:
            screen.line(line.p1, line.p2, "black", 2)


class Line(Obstacle):
    def __init__(self, p1, p2):
        super(Line, self).__init__()
        self.bounds = (ObstacleBase(p1, p2),)


class Rectangle(Obstacle):
    def __init__(self, left, top, width, height):
        super(Rectangle, self).__init__()
        self.top = top
        self.left = left
        self.bottom = top + height
        self.right = left + width

        self.bounds = (ObstacleBase(Vec2d(self.left, self.top),
                                    Vec2d(self.right, self.top)),
                       ObstacleBase(Vec2d(self.right, self.top),
                                    Vec2d(self.right, self.bottom)),
                       ObstacleBase(Vec2d(self.right, self.bottom),
                                    Vec2d(self.left, self.bottom)),
                       ObstacleBase(Vec2d(self.left, self.bottom),
                                    Vec2d(self.left, self.top))
                       )

    def render(self, screen):
        color = (130, 130, 130)
        screen.rect(self.top, self.left, self.bottom, self.right,
                    color=color, stroke_width=0)

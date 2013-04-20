from vector2d import Vec2d
from particle import Obstacle as ObstacleBase
import pygame


class Obstacle(object):
    def __init__(self):
        self.bounds = []

    def render(self, screen):
        color = pygame.Color("pink")
        for line in self.bounds:
            pygame.draw.line(screen, color, line.p1, line.p2)


class Line(Obstacle):
    def __init__(self, p1, p2):
        super(Line, self).__init__()
        self.bounds = (ObstacleBase(p1, p2),)


class Rectangle(Obstacle):
    def __init__(self, left, top, width, height):
        super(Rectangle, self).__init__()
        self._rect = pygame.Rect(left, top, width, height)  # for drawing

        bottom = top + height
        right = left + width

        self.bounds = (ObstacleBase(Vec2d(left, top), Vec2d(right, top)),
                        ObstacleBase(Vec2d(right, top), Vec2d(right, bottom)),
                        ObstacleBase(Vec2d(right, bottom), Vec2d(left, bottom)),
                        ObstacleBase(Vec2d(left, bottom), Vec2d(left, top)))

    def render(self, screen):
        color = (130, 130, 130)
        pygame.draw.rect(screen, color, self._rect, 0)

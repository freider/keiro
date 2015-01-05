import arty
from keiro.vector2d import Vec2d


class RRT(arty.Arty):
    def obstacle_velocity(self, pedestrian):
        return Vec2d(0, 0)  # don't extrapolate positions

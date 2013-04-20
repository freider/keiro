from pedestrian import Pedestrian
from keiro.vector2d import Vec2d
from keiro.geometry import line_distance2
import math
import random


class RandomWalkingAvoider(Pedestrian):
    step_mean = 200
    view_range = 25

    def __init__(self):
        Pedestrian.__init__(self)

    def think(self, dt, view, debugsurface):
        if self.waypoint_len() == 0:
            a = random.random() * math.pi * 2
            step = random.gauss(self.step_mean, self.step_mean / 3)
            self.waypoint_push(self.position + Vec2d(math.cos(a) * step, math.sin(a) * step))

        direction = self.waypoint().position - self.position
        for p in view.pedestrians:  # stop if any pedestrians are in the way
            if direction.angle(p.position - self.position) < math.pi / 2:
                self.waypoint_clear()
                return

        for o in view.obstacles:  # avoid obstacles
            if line_distance2(self.position, self.waypoint().position, o.p1, o.p2) <= self.radius ** 2:
                self.waypoint_clear()
                return


class RandomWalker(Pedestrian):
    step_mean = 200
    view_range = 0

    def __init__(self):
        Pedestrian.__init__(self)
        self.view_range = self.radius + 10

    def think(self, dt, view, debugsurface):
        if self.waypoint_len() == 0:
            a = random.random() * math.pi * 2
            step = random.gauss(self.step_mean, self.step_mean / 3)
            self.waypoint_push(self.position + Vec2d(math.cos(a) * step, math.sin(a) * step))

        for o in view.obstacles:  # avoid obstacles
            if line_distance2(self.position, self.waypoint().position, o.p1, o.p2) <= self.radius ** 2:
                self.waypoint_clear()
                return

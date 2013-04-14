import math
from keiro.scenario import Scenario
from fast.vector2d import Vec2d
from pedestrians.stubborn import Stubborn
from keiro.unit import Unit


class CrossingPaths(Scenario):
    """ Linear paths of the agent crosses a single pedestrian's

    A predictive algorithm should perform better than a non-predictive
    """

    def init(self):
        self.agent.position = Vec2d(200, 200)
        self.agent.goal = Vec2d(400, 200)
        self.agent.angle = 0

        u = Stubborn()
        u.position = Vec2d(300, 100)
        u.goal = Vec2d(300, 300)
        u.angle = math.pi / 2

        self.world.add_unit(u)


class BestToFollow(Scenario):
    world_size = (200, 100)
    walls = False

    def init(self):
        u = Unit()
        self.agent.position = Vec2d(20, 50)
        u.position = Vec2d(60, 50)
        self.agent.goal = Vec2d(180, 50)

        self.agent.angle = u.angle = 0

        u.waypoint_push(Vec2d(180, 50))
        u.waypoint_push(Vec2d(180, 90))
        self.world.add_unit(u)

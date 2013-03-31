import math
from scenario import Scenario
from fast.vector2d import Vec2d
from pedestrians.stubborn import Stubborn


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

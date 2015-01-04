import math
from keiro.scenario import Scenario
from keiro.vector2d import Vec2d
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

        u = Stubborn(random_seed=self.random.random())
        u.position = Vec2d(300, 100)
        u.goal = Vec2d(300, 300)
        u.angle = math.pi / 2

        self.world.add_unit(u)


class Empty(Scenario):
    """ Empty scenario for reference
    """

    def init(self):
        self.agent.position = Vec2d(100, 100)
        self.agent.goal = Vec2d(540, 380)
        self.agent.angle = 0


class BestToFollow(Scenario):
    """ Scenario where the optimal path is to follow a pedestrian

        The pedestrian walks to the target and then turns moves out
        of the way
    """
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


class PredictableCrowd(Scenario):
    world_size = (400, 400)

    def init(self):
        self.agent.position = Vec2d(50, 50)
        self.agent.goal = Vec2d(350, 350)
        for i in xrange(1, 10):
            u = Unit()
            xcoord = 50 + i * 30
            u.position = Vec2d(xcoord, 150)
            u.waypoint_push(Vec2d(xcoord, 200))
            u.waypoint_push(Vec2d(xcoord, 50))
            self.world.add_unit(u)


class BlockingCrowd(Scenario):
    world_size = (400, 400)

    def init(self):
        self.agent.position = Vec2d(50, 50)
        # self.agent.position = Vec2d(334.487305, 139.406128)
        # self.agent.angle = 0.994592547417
        self.agent.goal = Vec2d(350, 350)
        for i in xrange(1, 10):
            u = Unit()
            xcoord = 50 + i * 30
            u.position = Vec2d(xcoord, 150)
            self.world.add_unit(u)


class LonelyBlocking(Scenario):
    world_size = (400, 400)

    def init(self):
        self.agent.position = Vec2d(100, 200)
        # self.agent.position = Vec2d(334.487305, 139.406128)
        # self.agent.angle = 0.994592547417
        self.agent.goal = Vec2d(300, 200)
        u = Unit()
        u.position = Vec2d(200, 200)
        self.world.add_unit(u)


class SelfBattle(Scenario):
    world_size = (400, 400)

    def init(self):
        self.agent.position = Vec2d(100, 200)
        self.agent.angle = 0
        self.agent.goal = Vec2d(300, 200)
        from agents.voronoimap import VoronoiMap
        from agents.arty import Arty
        u = Arty(0)
        u.position = Vec2d(300, 200)
        u.goal = Vec2d(100, 200)
        u.angle = math.pi
        self.world.add_unit(u)

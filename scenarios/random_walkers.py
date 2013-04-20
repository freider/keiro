from keiro.scenario import Scenario
from keiro.vector2d import Vec2d
from pedestrians.randomwalker import RandomWalkingAvoider


class RandomWalkers(Scenario):
    world_size = (640, 480)

    def init(self):
        if self.parameter is None:
            self.parameter = 50

        # start is upper left corner
        self.agent.position = Vec2d(10, 10)
        # goal is lower right
        self.agent.goal = Vec2d(*self.world.size) - self.agent.position
        self.agent.angle = (self.agent.goal - self.agent.position).angle()

        for i in xrange(self.parameter):
            init_position = self.agent.position
            while init_position.distance_to(self.agent.position) < 20:
                init_position = Vec2d(self.random.randrange(self.world.size[0]),
                                      self.random.randrange(self.world.size[1]))
            u = RandomWalkingAvoider()
            u.position = init_position
            self.world.add_unit(u)

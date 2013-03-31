import random
from scenario import Scenario
from fast.vector2d import Vec2d
import obstacle
from pedestrians.randomwalker import RandomWalkingAvoider


class Maze(Scenario):
    world_size = (640, 480)


    def init(self):
        if parameter is None:
            parameter = 50

        self.agent.position = Vec2d(200, 200)
        self.agent.goal = Vec2d(400, 200)
        self.agent.angle = 0

        self.world.add_obstacle(
            obstacle.Line(Vec2d(100, 100), Vec2d(100, 300))
        )
        self.world.add_obstacle(
            obstacle.Line(Vec2d(100, 300), Vec2d(500, 300))
        )
        self.world.add_obstacle(
            obstacle.Line(Vec2d(500, 300), Vec2d(500, 100))
        )
        self.world.add_obstacle(
            obstacle.Line(Vec2d(500, 100), Vec2d(100, 100))
        )
        self.world.add_obstacle(
            obstacle.Line(Vec2d(300, 100), Vec2d(300, 250))
        )

        for m in xrange(parameter):
            good = False
            u = RandomWalkingAvoider()

            # generate random positions for pedestrians
            # that are not inside obstacles...
            while not good:
                init_position = Vec2d(
                    random.randrange(u.radius + 1, self.world.size[0] - u.radius - 1),
                    random.randrange(u.radius + 1, self.world.size[1] - u.radius - 1)
                )
                good = init_position.distance_to(self.agent.position) > 20

            u.position = init_position
            self.world.add_unit(u)

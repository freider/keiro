from keiro.scenario import Scenario
from keiro.vector2d import Vec2d
from keiro import obstacle
from pedestrians.randomwalker import RandomWalkingAvoider
from keiro.geometry import linesegdist2


class Maze(Scenario):
    world_size = (640, 480)

    def init(self):
        if self.parameter is None:
            self.parameter = 10

        self.agent.position = Vec2d(200, 200)
        self.agent.goal = Vec2d(400, 200)
        self.agent.angle = 0

        shapes = [
            [
                Vec2d(100, 100),
                Vec2d(100, 380),
                Vec2d(500, 380),
                Vec2d(500, 100),
                Vec2d(100, 100),
            ],
            [
                Vec2d(300, 100),
                Vec2d(300, 250),
            ],
            [
                Vec2d(200, 250),
                Vec2d(400, 250),
            ]
        ]

        for shape in shapes:
            last = shape[0]
            for point in shape:
                self.world.add_obstacle(obstacle.Line(last, point))
                last = point

        for m in xrange(self.parameter):
            good = False
            u = RandomWalkingAvoider()

            # generate random positions for pedestrians
            # that are not inside obstacles...
            while not good:
                init_position = Vec2d(
                    self.random.randrange(100 + u.radius + 1, 500 - u.radius - 1),
                    self.random.randrange(100 + u.radius + 1, 380 - u.radius - 1),
                )
                good = init_position.distance_to(self.agent.position) > 20
                for shape in shapes:
                    last = shape[0]
                    for point in shape:
                        if linesegdist2(
                            last, point,
                            init_position
                        ) < u.radius ** 2:
                            good = False
                            break
                        last = point
                    if not good:
                        break

            u.position = init_position
            self.world.add_unit(u)

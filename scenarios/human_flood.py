import random
from keiro.scenario import Spawner
from keiro.vector2d import Vec2d
from pedestrians.stubborn import Stubborn


class TheFlood(Spawner):
    world_size = (640, 480)
    crowd_rate = 3

    def init(self):
        agent = self.agent
        agent.position = Vec2d(agent.radius * 2, self.world.size[1] / 2)
        agent.goal = Vec2d(self.world.size[0] - agent.radius * 2, self.world.size[1] / 2)
        agent.angle = (agent.goal - agent.position).angle()

    def spawn(self, num_units):
        for u in self.world.units:
            if u is not self.agent and u.position.distance_to(u.goal) < 1:
                self.world.remove_unit(u)

        for i in xrange(num_units):
            u = Stubborn()

            u.position = Vec2d(
                self.world.size[0] - u.radius - 1,
                random.randrange(u.radius, self.world.size[1] - u.radius)
            )

            while u.position.distance_to(self.agent.goal) < 5 * self.agent.radius:
                u.position = Vec2d(
                    self.world.size[0] - u.radius - 1,
                    random.randrange(u.radius, self.world.size[1] - u.radius)
                )

            u.goal = Vec2d(
                u.radius + 1,
                random.randrange(u.radius, self.world.size[1] - u.radius)
            )
            u.angle = (u.goal - u.position).angle()

            self.world.add_unit(u)

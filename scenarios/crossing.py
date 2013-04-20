from keiro.scenario import Spawner
from keiro.vector2d import Vec2d
from pedestrians.stubborn import Stubborn


class Crossing(Spawner):
    world_size = (640, 480)
    crowd_rate = 3

    def init(self):
        self.agent.position = Vec2d(10, self.world.size[1] / 2)
        self.agent.goal = Vec2d(self.world.size[0] - 10, self.world.size[1] / 2)
        self.agent.angle = (self.agent.goal - self.agent.position).angle()

        agent_travel = self.agent.goal - self.agent.position
        self.agent.travel_length = agent_travel.length()

    def random_xpos(self, unit):
        return self.random.randrange(
            unit.radius + 1,
            self.world.size[0] - unit.radius - 1
        )

    def random_ypos(self, unit):
        return self.random.randrange(
            unit.radius + 1,
            self.world.size[1] - unit.radius - 1
        )

    def spawn(self, num_units):
        for u in self.world.units:
            if u is not self.agent and u.position.distance_to(u.goal) <= u.radius:
                self.world.remove_unit(u)
                avg_groundspeed = u.travel_length / (self.world._time - u.spawn_time)
                self.world.avg_groundspeed_list.append(avg_groundspeed)
                self.world.collision_list.append(u.collisions)
                #print ["Pedestrian Speed:", avg_groundspeed]
                #print ["Number of collisions:", u.collisions]

        for i in xrange(num_units):
            u = Stubborn()

            if self.random.random() < 0.5:  # coin toss
                # "horizontal" movement
                p1 = Vec2d(u.radius + 1, self.random_ypos(u))
                p2 = Vec2d(
                    self.world.size[0] - u.radius - 1,
                    self.random_ypos(u)
                )
            else:
                # "vertical" movement
                p1 = Vec2d(self.random_xpos(u), u.radius + 1)
                p2 = Vec2d(
                    self.random_xpos(u),
                    self.world.size[1] - u.radius - 1
                )

            if self.random.random() < 0.5:  # coin toss
                u.position = p1
                u.goal = p2
                u.angle = (p2 - p1).angle()
            else:
                u.position = p2
                u.goal = p1
                u.angle = (p1 - p2).angle()

            travel = u.goal - u.position
            u.travel_length = travel.length()
            u.spawn_time = self.world._time
            self.world.add_unit(u)

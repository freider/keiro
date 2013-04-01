from fast.vector2d import Vec2d
import obstacle
import pygame
import random
from world import World


class ScenarioRegistrar (type):
    """Registers all scenarios that are declared, to let the user choose"""
    register = {}

    def __new__(cls, name, bases, dct):
        assert name not in ScenarioRegistrar.register, 'Multiple scenarios %r defined!' % name
        ret = ScenarioRegistrar.register[name] = type.__new__(cls, name, bases, dct)
        return ret


class Scenario(object):  # abstract
    __metaclass__ = ScenarioRegistrar
    world_size = (640, 480)  # Override this to customize world size
    walls = True

    def __init__(self, parameter, agent):
        self.parameter = parameter
        self.agent = agent
        self.world = World(self.world_size)
        self.world.init()
        self.init()

        if self.walls:
            self.add_walls()

        self.world.add_unit(agent)

    def add_walls(self):
        """ Convenience method to add obstacles along all borders of the rendered world.

        Call this when setting up the world to prevent units from "escaping"
        """
        self.world.add_obstacle(obstacle.Line(Vec2d(0, 0), Vec2d(0, self.world_size[1])))
        self.world.add_obstacle(obstacle.Line(Vec2d(0, self.world_size[1]), Vec2d(self.world_size[0], self.world_size[1])))
        self.world.add_obstacle(obstacle.Line(Vec2d(self.world_size[0], self.world_size[1]), Vec2d(self.world_size[0], 0)))
        self.world.add_obstacle(obstacle.Line(Vec2d(self.world_size[0], 0), Vec2d(0, 0)))

    def update(self, dt):
        pass

    def run(self):
        overtime = -1
        agent_out_time = 0
        while 1:
            if self.agent.position.distance_to(self.agent.goal) <= self.agent.radius:
                ## for Crossing scenario only
                if (agent_out_time == 0):
                    self.world.remove_unit(self.agent)
                    agent_out_time = self.world._time
                overtime = overtime + 1
                if overtime == 0:
                    if(len(self.world.avg_groundspeed_list)):
                        print "Average Average Ground Speed:", sum(self.world.avg_groundspeed_list) / len(self.world.avg_groundspeed_list)
                        print "Agent Ground Speed:", self.agent.travel_length / agent_out_time
                    if(len(self.world.collision_list)):
                        print "Average Collisions:", sum(self.world.collision_list) / len(self.world.collision_list)
                        print "Agent Collisions:", self.agent.collisions
                    return True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False

            dt = self.world.advance()
            self.update(dt)


class Spawner(Scenario):
    crowd_rate = 0

    def __init__(self, parameter, agent):
        super(Spawner, self).__init__(parameter, agent)
        if self.parameter is not None:
            self.crowd_rate = self.parameter

    def update(self, dt):
        super(Spawner, self).update(dt)
        exact = dt * self.crowd_rate
        numtospawn = int(exact)
        exact -= numtospawn
        if random.random() <= exact:
            numtospawn += 1
        self.spawn(numtospawn)

    def spawn(self, num_units):
        pass

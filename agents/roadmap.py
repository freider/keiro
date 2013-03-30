import pygame
import random
from agent import Agent
import graphbuilder
from fast import astar
from fast.geometry import linesegdist2
from fast.vector2d import Vec2d


class RoadMap(Agent):
    FREEMARGIN = 1

    def __init__(self, parameter):
        if parameter is None:
            parameter = 10
        super(RoadMap, self).__init__(parameter)
        self.NODES = parameter
        self.cdist = 10000000

    def think(self, dt, view, debugsurface):
        if not self.goal:  # have no goal?
            return
        #debugsurface.fill((255, 0, 0, 100))
        ccourse = False
        last = self.position
        for i in xrange(self.waypoint_len()):
            for o in view.pedestrians:
                if linesegdist2(last, self.waypoint(i).position, o.position) <= (self.radius + o.radius + self.FREEMARGIN) ** 2:
                    ccourse = True
                    break
            last = self.waypoint(i).position
            if ccourse:
                break

        gb = graphbuilder.GraphBuilder(self.speed, self.turningspeed)

        safe_distance = self.radius + self.FREEMARGIN  # some margin is nice
        start = gb.node(self.position, self.angle)
        end = gb.node(self.goal, None)

        if graphbuilder.free_path(self.position, self.goal, view, safe_distance):
            gb.connect(self.position, self.goal)
        else:
            for i in xrange(self.NODES / 2):  # global planning
                newpos = Vec2d(640 * random.random(), 480 * random.random())
                for pos in gb.positions():
                    if graphbuilder.free_path(Vec2d(*pos), newpos, view, safe_distance):
                        gb.connect(pos, newpos)
                        pygame.draw.aaline(debugsurface, (0, 255, 0, 255), pos, newpos)

            for i in xrange(self.NODES - self.NODES / 2):  # some extra local points to handle the crowd
                newpos = self.position + Vec2d((2 * random.random() - 1) * self.view_range, (2 * random.random() - 1) * self.view_range)
                for pos in gb.positions():
                    if graphbuilder.free_path(Vec2d(*pos), newpos, view, safe_distance):
                        gb.connect(pos, newpos)
                        pygame.draw.aaline(debugsurface, (0, 255, 0, 255), pos, newpos)

            for p in gb.positions():
                pygame.draw.circle(debugsurface, (0, 0, 0), map(int, p), 2, 0)

        nodes = gb.all_nodes()
        result = astar.shortest_path(start, end, nodes)
        if result.success:
            result.path = [tuple(self.position)]
            for i in result.indices:
                if result.path[-1] != nodes[i].position:
                    result.path.append(nodes[i].position)

        if ccourse is True:
            self.waypoint_clear()

        if result.success is True and (self.waypoint_len() == 0 or result.total_cost < self.cdist):
            self.waypoint_clear()
            for p in result.path:
                self.waypoint_push(Vec2d(*p))
            self.cdist = result.total_cost

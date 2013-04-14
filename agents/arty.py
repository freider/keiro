import pygame
import math
from agent import Agent
from fast.vector2d import Vec2d
from fast.geometry import linesegdist2, line_distance2, angle_diff
from stategenerator import ExtendingGenerator, StateGenerator, PrependedGenerator


class TestGenerator(PrependedGenerator):
    def __init__(self, *args):
        super(TestGenerator, self).__init__(*args)
        self.first = True

    def generate(self):
        self.first = not self.first
        if self.first:
            return Vec2d(300, 250)
        else:
            return Vec2d(300, 150)


class Arty(Agent):
    SAFETY_THRESHOLD = 0.9  # this has practically no effect in the current implementation
    GLOBALMAXEDGE = 70
    LOCALMAXEDGE = 50
    LOCALMAXSIZE = 10
    FREEMARGIN = 2

    class Node:
        def __init__(self, position, angle, parent, time=None, freeprob=None):
            self.position = position
            self.angle = angle
            self.time = time
            self.parent = parent
            self.freeprob = freeprob

    def __init__(self, parameter):
        if parameter is None:
            parameter = 60
        super(Arty, self).__init__(parameter)
        self.GLOBALNODES = parameter

    def globaltree(self, view):
        #RRT from goal
        nodes = [self.Node(self.goal, None, None)]
        sg = StateGenerator(0, 640, 0, 480)  # TODO: remove hardcoded world size

        for newpos in sg.generate_n(self.GLOBALNODES):
            besttime = None
            bestnode = None
            for tonode in nodes:
                topos = tonode.position
                connectable = True
                for o in view.obstacles:
                    if line_distance2(topos, newpos, o.p1, o.p2) < (self.radius + self.FREEMARGIN) ** 2:
                        connectable = False
                        break

                if connectable:
                    dist = topos.distance_to(newpos)
                    if tonode.parent is None:
                        turndist = 0  # goal node
                    else:
                        turndist = abs(angle_diff((topos - newpos).angle(), tonode.angle))
                    time = dist / self.speed + turndist / self.turningspeed

                    if bestnode is None or time < besttime:
                        besttime = time
                        bestnode = tonode

            if bestnode:
                topos = bestnode.position
                diff = newpos - topos
                angle = diff.angle()
                difflen = diff.length()
                div = int(math.ceil(difflen / self.GLOBALMAXEDGE))
                prev = bestnode
                #subdivide the new edge
                for d in xrange(1, div + 1):
                    newnode = self.Node(topos + diff * d / div, angle, prev)
                    nodes.append(newnode)
                    prev = newnode

        self.globalnodes = nodes
        print "Done building global roadmap tree", len(self.globalnodes)

    def init(self, view):
        """Builds the static obstacle map, global roadmap"""
        self.globaltree(view)

    def future_position(self, pedestrian, time):
        pos = pedestrian.position + pedestrian.velocity * time
        #pygame.draw.line(self.debugsurface, (255, 0, 0), pedestrian.position, pos)
        return pos

    def freeprob_pedestrians(self, position, view, time):
        """Returns probability that specified position will be collision free at specified time with respect to pedestrians"""
        for p in view.pedestrians:
            pedestrianpos = self.future_position(p, time)  # extrapolated position
            if position.distance_to(pedestrianpos) < (self.radius + p.radius + self.FREEMARGIN):
                self.freeprob_fail_pedestrian = p
                return 0  # collision with pedestrian
        return 1

    def freeprob_turn(self, position, a1, a2, view, starttime):
        """ Probability that a turn started at starttime at position between angles a1 and a2 will be collision free """
        dur = abs(angle_diff(a1, a2)) / self.turningspeed
        for p in view.pedestrians:
            p1 = p.position
            p2 = self.future_position(p, dur)  # extrapolate
            if linesegdist2(p1, p2, position) < (self.radius + p.radius + self.FREEMARGIN) ** 2:
                self.freeprob_fail_pedestrian = p
                return 0
        return 1

    def freeprob_line(self, p1, p2, view, starttime):
        """ Free probability for moving from p1 to p2 starting on starttime """
        if p1 == p2:
            return self.freeprob_pedestrians(p1, view, starttime)

        for o in view.obstacles:
            if line_distance2(o.p1, o.p2, p1, p2) < (self.radius + self.FREEMARGIN) ** 2:
                return 0

        diff = p2 - p1
        length = diff.length()
        v = diff / length
        resolution = self.radius * 2
        numsegments = int(math.ceil(length / resolution))
        segmentlen = length / numsegments
        timediff = segmentlen / self.speed

        freeprob = 1.0
        for i in xrange(numsegments + 1):
            freeprob *= self.freeprob_pedestrians(p1 + v * i * segmentlen, view, starttime + i * timediff)

        return freeprob

    def freeprob_turn_line(self, p1, a1, p2, view, starttime):
        """Free probability for turning and then walking on a straight line"""
        a2 = (p2 - p1).angle()
        dt = abs(angle_diff(a1, a2)) / self.turningspeed
        free = self.freeprob_turn(p1, a1, a2, view, starttime)
        free *= self.freeprob_line(p1, p2, view, starttime + dt)
        return free

    def segment_time(self, a1, p1, p2):
        """Returns time to get from a state (a1, p1) to ((p2-p1).angle(), p2)"""
        diff = p2 - p1
        turningtime = abs(angle_diff(a1, diff.angle())) / self.turningspeed
        movetime = diff.length() / self.speed
        return turningtime + movetime

    def getpath(self, view):
        """Use the ART algorithm to get a path to the goal"""
        if self.goal_occupied(view):
            return
        #first try to find global node by local planner from current position
        testpath, testtime = self.find_globaltree(self.position, self.angle, view, 0.0, 1.0)
        if testpath:
            return testpath
        print "Cannot find safe global path from current, extending search tree"
        start = Arty.Node(self.position, self.angle, parent=None, time=0, freeprob=1)
        nodes = [start]

        # TODO: add unit test to see that last iteration gets reused
        states = ExtendingGenerator(
            (self.position.x - self.view_range,
             self.position.x + self.view_range,
             self.position.y - self.view_range,
             self.position.y + self.view_range
             ),
            (0, 640, 0, 480),  # TODO: remove hardcoded world size)
            10)  # arbitrarily chosen

        #always try to use the nodes from the last solution in this iterations
        #so they are kept if still the best
        for i in xrange(self.waypoint_len()):
            pos = self.waypoint(i).position
            #if pos.distance_to(self.position) <= self.radius:
            states.prepend(pos)

        bestsolution = None
        bestsolution_time = None

        for nextpos in states.generate_n(self.LOCALMAXSIZE):
            bestparent = None
            besttime = None
            for n in nodes:
                freeprob = self.freeprob_turn_line(n.position, n.angle, nextpos, view, n.time)
                newprob = n.freeprob * freeprob
                if newprob < self.SAFETY_THRESHOLD:
                    continue
                endtime = n.time + self.segment_time(n.angle, n.position, nextpos)

                if bestparent is None or endtime < besttime:
                    bestparent = n
                    besttime = endtime

            if bestparent is not None:
                pygame.draw.line(self.debugsurface, (0, 255, 0), bestparent.position, nextpos)
                #subdivide the new edge
                diff = nextpos - bestparent.position
                angle = diff.angle()
                difflen = diff.length()
                div = int(math.ceil(difflen / self.LOCALMAXEDGE))

                lastnode = bestparent

                for d in xrange(1, div + 1):
                    #add new node and subdivisions to new graph
                    subpos = bestparent.position + diff * d / div
                    freeprob = self.freeprob_turn_line(lastnode.position, lastnode.angle, subpos, view, lastnode.time)
                    dt = self.segment_time(lastnode.angle, lastnode.position, subpos)
                    newnode = self.Node(subpos, angle, parent=lastnode, time=lastnode.time + dt, freeprob=lastnode.freeprob * freeprob)
                    lastnode = newnode
                    nodes.append(newnode)

                    #get the best path to the global graph on to the goal from the new node
                    gpath, gtime = self.find_globaltree(newnode.position, newnode.angle, view, newnode.time, newnode.freeprob)
                    if gpath is not None:
                        if bestsolution is None or gtime < bestsolution_time:
                            path = []
                            n = newnode
                            while n is not None:
                                path.append(n.position)
                                n = n.parent
                            path.reverse()

                            for gpos in gpath:
                                path.append(gpos)

                            bestsolution = path
                            bestsolution_time = gtime
        return bestsolution

    def find_globaltree(self, p1, a1, view, time, startprob):
        """Tries to reach global tree from position/angle

            Returns (path, time) to get to goal"""

        bestpath = None
        besttime = None

        for n in self.globalnodes:
            free = startprob * self.freeprob_turn_line(p1, a1, n.position, view, time)
            if free < self.SAFETY_THRESHOLD:
                pygame.draw.circle(self.debugsurface, pygame.Color("blue"), map(int, n.position), 8, 2)

            t = time + self.segment_time(a1, p1, n.position)
            a2 = (n.position - p1).angle()
            #try to reach goal from global node
            path = []
            cur = n
            while cur.parent is not None and free >= self.SAFETY_THRESHOLD:
                path.append(cur.position)
                self.freeprob_fail_pedestrian = None
                free *= self.freeprob_turn_line(cur.position, a2, cur.parent.position, view, t)
                if free < self.SAFETY_THRESHOLD:
                    pygame.draw.aaline(
                        self.debugsurface,
                        pygame.Color("pink"),
                        n.position,
                        cur.position,
                        3
                    )
                    if self.freeprob_fail_pedestrian:
                        pygame.draw.aaline(
                            self.debugsurface,
                            pygame.Color("pink"),
                            cur.position,
                            self.freeprob_fail_pedestrian.position,
                            3
                        )
                        pygame.draw.circle(
                            self.debugsurface,
                            pygame.Color("red"),
                            map(int, self.freeprob_fail_pedestrian.position),
                            10,
                            2
                        )

                t += self.segment_time(a2, cur.position, cur.parent.position)
                a2 = (cur.parent.position - cur.position).angle()
                cur = cur.parent

            if free < self.SAFETY_THRESHOLD:
                pygame.draw.circle(self.debugsurface, pygame.Color("pink"), map(int, n.position), 5, 2)
                continue

            path.append(cur.position)

            if bestpath is None or t < besttime:
                bestpath = path
                besttime = t

        return (bestpath, besttime)

    def think(self, dt, view, debugsurface):
        if not self.goal:
            return
        self.view = view
        self.debugsurface = debugsurface

        # draw the global roadmap
        for n in self.globalnodes:
            if n.parent:
                pygame.draw.line(debugsurface, pygame.Color("black"), n.position, n.parent.position)
            pygame.draw.circle(debugsurface, pygame.Color("red"), map(int, n.position), 2, 0)

        # mark visible pedestrians
        for p in view.pedestrians:
            pygame.draw.circle(debugsurface, pygame.Color("green"), map(int, p.position), int(p.radius) + 2, 2)

        path = self.getpath(view)
        self.waypoint_clear()

        if path:
            for p in path:
                self.waypoint_push(p)

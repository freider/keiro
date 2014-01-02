import math
from keiro.agent import Agent
from keiro.vector2d import Vec2d
from keiro.geometry import linesegdist2, line_distance2, angle_diff
from keiro.stategenerator import ExtendingGenerator, StateGenerator
from keiro.stategenerator import PrependedGenerator


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


class Node:
    def __init__(self, position, angle, parent, time=None, freeprob=None):
        self.position = position
        self.angle = angle
        self.time = time
        self.parent = parent
        self.freeprob = freeprob


class RoadMapGenerator(object):
    """Creates roadmap that covers the static environment.

    Implemented using RRT expanded from the goal.
    Call once after a new target has been assigned.
    """

    def __init__(self, view, goal, min_distance,
                 speed, turningspeed, max_edge_length):
        self.view = view
        self.goal = goal
        self.min_distance = min_distance
        self.min_distance2 = min_distance ** 2
        self.speed = speed
        self.turningspeed = turningspeed
        self.max_edge_length = max_edge_length
        self.nodes = [Node(self.goal, None, None)]

    def line_is_traversable(self, p1, p2):
        """Check if line is collision free with static obstacles

        Returns True if a straight path between p1 and p2 is possible without
        colliding into static obstacles
        """
        for o in self.view.obstacles:
            if line_distance2(p1, p2, o.p1, o.p2) < self.min_distance2:
                return False
        return True

    def _traversal_time(self, candidate_position, existing_node):
        distance = candidate_position.distance_to(existing_node.position)
        if existing_node.parent is None:
            # existing_node is goal node
            #i.e. once it's reached, we don't have to turn
            turndist = 0
        else:
            movement_vector = (existing_node.position - candidate_position)
            turndist = abs(
                angle_diff(movement_vector.angle(), existing_node.angle)
            )
        line_dt = distance / self.speed
        turn_dt = turndist / self.turningspeed
        traversal_time = line_dt + turn_dt
        return traversal_time

    def _connect_node(self, existing_node, new_position):
        # reversed traversal vector
        diff = new_position - existing_node.position
        # direction should be traversal direction
        angle = (existing_node.position - new_position).angle()
        n_subdivisions = int(math.ceil(diff.length() / self.max_edge_length))
        next_node = existing_node
        #subdivide the new edge
        for d in xrange(1, n_subdivisions + 1):
            newnode = Node(
                existing_node.position + (diff * d / n_subdivisions),
                angle,
                next_node
            )
            self.nodes.append(newnode)
            next_node = newnode

    def _connect_to_best(self, candidate_position):
        best_traversal_time = None
        best_node = None
        for existing_node in self.nodes:
            existing_node_position = existing_node.position

            if self.line_is_traversable(
                    candidate_position, existing_node_position):
                # check if this existing node is the one that
                # can be reached the fastest from the candidate
                traversal_time = self._traversal_time(candidate_position,
                                                      existing_node)
                if best_node is None or traversal_time < best_traversal_time:
                    best_traversal_time = traversal_time
                    best_node = existing_node

        if best_node:
            # generated state can be connected to some existing node
            self._connect_node(best_node, candidate_position)

    def run(self, iterations):
        sg = StateGenerator(*self.view.world_bounds)

        for candidate_position in sg.generate_n(iterations):
            self._connect_to_best(candidate_position)

    def get_nodes(self):
        return self.nodes


class Arty(Agent):
    SAFETY_THRESHOLD = 0.9  # has no effect in the current implementation
    GLOBALMAXEDGE = 70
    LOCALMAXEDGE = 50
    LOCALMAXSIZE = 10
    FREEMARGIN = 2

    def __init__(self, parameter):
        if parameter is None:
            parameter = 60
        super(Arty, self).__init__(parameter)
        self.GLOBALNODES = parameter

    def init(self, view):
        """Builds the static obstacle map, global roadmap"""
        self.build_global_roadmap(view)

    def build_global_roadmap(self, view):
        generator = RoadMapGenerator(
            view,
            self.goal,
            self.radius + self.FREEMARGIN,
            self.speed,
            self.turningspeed,
            self.GLOBALMAXEDGE
        )
        generator.run(self.GLOBALNODES)
        self.globalnodes = generator.get_nodes()
        print "Done building global roadmap tree", len(self.globalnodes)

    def think(self, dt, view, debugsurface):
        if not self.goal:
            return
        self.view = view
        self.debugsurface = debugsurface

        # draw the global roadmap
        for n in self.globalnodes:
            if n.parent:
                debugsurface.line(
                    n.position,
                    n.parent.position,
                    "black",
                    2
                )
            debugsurface.circle(
                n.position,
                2,
                "black",
                0
            )

        # mark visible pedestrians
        for p in view.pedestrians:
            debugsurface.circle(p.position, p.radius + 2, "green", 2)

        path = self.getpath(view)
        self.waypoint_clear()

        if path:
            for p in path:
                self.waypoint_push(p)

    def future_position(self, pedestrian, time):
        pos = pedestrian.position + pedestrian.velocity * time
        #pygame.draw.line(self.debugsurface,
        #                 (255, 0, 0),
        #                 pedestrian.position,
        #                 pos)
        return pos

    def freeprob_pedestrians(self, position, view, time):
        """Probability that position will be collision free

        At specified time with respect to pedestrians in view
        """
        for p in view.pedestrians:
            # extrapolate position
            pedestrianpos = self.future_position(p, time)
            safe_dist = (self.radius + p.radius + self.FREEMARGIN)
            if position.distance_to(pedestrianpos) < safe_dist:
                self.freeprob_fail_pedestrian = p
                return 0  # collision with pedestrian
        return 1

    def freeprob_turn(self, position, a1, a2, view, starttime):
        """ Probability that a turn is collision free

            Started at starttime at position between
            angles a1 and a2.
        """
        dur = abs(angle_diff(a1, a2)) / self.turningspeed
        for p in view.pedestrians:
            # extrapolate to start of turn
            p1 = self.future_position(p, starttime)
            # extrapolate to end of turn
            p2 = self.future_position(p, starttime + dur)
            safedist2 = (self.radius + p.radius + self.FREEMARGIN) ** 2
            if linesegdist2(p1, p2, position) < safedist2:
                self.freeprob_fail_pedestrian = p
                return 0
        return 1

    def freeprob_line(self, p1, p2, view, starttime):
        """ Free probability for moving from p1 to p2 starting on starttime """
        if p1 == p2:
            return self.freeprob_pedestrians(p1, view, starttime)

        safedist2 = (self.radius + self.FREEMARGIN) ** 2

        for o in view.obstacles:
            if line_distance2(o.p1, o.p2, p1, p2) < safedist2:
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
            passed_position = p1 + v * i * segmentlen
            passing_time = starttime + i * timediff
            freeprob *= self.freeprob_pedestrians(
                passed_position, view, passing_time
            )

        return freeprob

    def freeprob_turn_line(self, p1, a1, p2, view, starttime):
        """Free probability for turning and then walking on a straight line"""
        a2 = (p2 - p1).angle()
        dt = abs(angle_diff(a1, a2)) / self.turningspeed
        free = self.freeprob_turn(p1, a1, a2, view, starttime)
        free *= self.freeprob_line(p1, p2, view, starttime + dt)
        return free

    def segment_time(self, a1, p1, p2):
        """Time to get from a state (a1, p1) to ((p2-p1).angle(), p2)"""
        diff = p2 - p1
        turningtime = abs(angle_diff(a1, diff.angle())) / self.turningspeed
        movetime = diff.length() / self.speed
        return turningtime + movetime

    def getpath(self, view):
        """Use the ART algorithm to get a path to the goal"""
        if self.goal_occupied(view):
            # TODO: choose another point on the global map
            #       that is closer to the goal than self.position
            return
        #first try to find global node by straight line from current position
        testpath, testtime = self.find_globaltree(
            self.position, self.angle, view, start_time=0.0, start_prob=1.0
        )
        if testpath:
            return testpath
        print "No safe global path - initializing local search"
        start = Node(self.position, self.angle,
                     parent=None, time=0, freeprob=1)
        nodes = [start]

        # TODO: add unit test to see that last iteration gets reused
        states = ExtendingGenerator(
            (self.position.x - self.view_range,
             self.position.x + self.view_range,
             self.position.y - self.view_range,
             self.position.y + self.view_range
             ),
            view.world_bounds,
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
                freeprob = self.freeprob_turn_line(
                    n.position, n.angle, nextpos, view, n.time
                )
                newprob = n.freeprob * freeprob
                if newprob < self.SAFETY_THRESHOLD:
                    continue
                segment_time = self.segment_time(n.angle, n.position, nextpos)
                endtime = n.time + segment_time

                if bestparent is None or endtime < besttime:
                    bestparent = n
                    besttime = endtime

            if bestparent is not None:
                self.debugsurface.line(
                    bestparent.position,
                    nextpos,
                    (0, 255, 0),
                )
                #subdivide the new edge
                diff = nextpos - bestparent.position
                angle = diff.angle()
                difflen = diff.length()
                div = int(math.ceil(difflen / self.LOCALMAXEDGE))

                lastnode = bestparent

                for d in xrange(1, div + 1):
                    #add new node and subdivisions to new graph
                    subpos = bestparent.position + diff * d / div
                    freeprob = self.freeprob_turn_line(
                        lastnode.position,
                        lastnode.angle,
                        subpos,
                        view,
                        lastnode.time
                    )
                    dt = self.segment_time(
                        lastnode.angle,
                        lastnode.position,
                        subpos
                    )
                    newnode = Node(
                        subpos, angle,
                        parent=lastnode,
                        time=lastnode.time + dt,
                        freeprob=lastnode.freeprob * freeprob
                    )
                    lastnode = newnode
                    nodes.append(newnode)

                    #get the best path to the global graph
                    #on to the goal from the new node
                    gpath, gtime = self.find_globaltree(
                        newnode.position,
                        newnode.angle,
                        view,
                        newnode.time,
                        newnode.freeprob
                    )
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

    def find_globaltree(self, from_position, from_angle,
                        view, start_time, start_prob):
        """Tries to reach global tree from position/angle

            Returns (path, time) to get to goal"""

        best_path = None
        best_time_to_goal = None

        for global_candidate in self.globalnodes:
            free_prob, path, time_to_goal = self.find_globalnode(
                global_candidate,
                from_position,
                from_angle,
                view,
                start_time=start_time,
                start_prob=start_prob
            )

            if free_prob < self.SAFETY_THRESHOLD:
                self.debugsurface.line(
                    from_position,
                    global_candidate.position,
                    "red",
                    2
                )
                continue

            if best_path is None or time_to_goal < best_time_to_goal:
                best_path = path
                best_time_to_goal = time_to_goal

        return (best_path, best_time_to_goal)

    def find_globalnode(self, global_candidate, from_position,
                        from_angle, view, start_time, start_prob):
        # get to global node
        free = start_prob * self.freeprob_turn_line(
            from_position,
            from_angle,
            global_candidate.position,
            view,
            start_time
        )
        # is that first straight segment safe?
        if free < self.SAFETY_THRESHOLD:
            self.debugsurface.line(
                from_position,
                global_candidate.position,
                "red"
            )

        # update node and time to reflect new position/time
        current_node = global_candidate
        time_to_candidate = self.segment_time(
            from_angle,
            from_position,
            global_candidate.position
        )
        current_time = start_time + time_to_candidate

        current_angle = (global_candidate.position - from_position).angle()

        # follow global tree to goal, and check for collisions
        path = [current_node.position]

        while current_node.parent and free >= self.SAFETY_THRESHOLD:
            self.freeprob_fail_pedestrian = None
            free *= self.freeprob_turn_line(
                current_node.position,
                current_angle,
                current_node.parent.position,
                view,
                current_time
            )
            if free < self.SAFETY_THRESHOLD:
                self.debugsurface.line(
                    global_candidate.position,
                    current_node.position,
                    "pink",
                    3
                )
                if self.freeprob_fail_pedestrian:
                    self.debugsurface.line(
                        current_node.position,
                        self.freeprob_fail_pedestrian.position,
                        "pink",
                        3
                    )
                    self.debugsurface.circle(
                        self.freeprob_fail_pedestrian.position,
                        10,
                        "red",
                        2
                    )

            current_time += self.segment_time(
                current_angle,
                current_node.position,
                current_node.parent.position
            )
            current_direction = \
                current_node.parent.position - current_node.position
            current_angle = current_direction.angle()
            current_node = current_node.parent
            path.append(current_node.position)
        return free, path, current_time

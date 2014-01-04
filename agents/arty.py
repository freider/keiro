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
    def __init__(self, position, angle, parent, time=None, safeness=None):
        self.position = position
        self.angle = angle
        self.time = time
        self.parent = parent
        self.safeness = safeness


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
        self.nodes = [Node(self.goal, None, None, 0)]

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
            subpos = existing_node.position + (diff * d / n_subdivisions)
            total_time = next_node.time + self._traversal_time(
                subpos,
                next_node
            )

            newnode = Node(
                subpos,
                angle,
                next_node,
                total_time
            )
            self.nodes.append(newnode)
            #next_node = newnode

    def _connect_to_best(self, candidate_position):
        best_total_time = None
        best_node = None
        for existing_node in self.nodes:
            existing_node_position = existing_node.position

            if self.line_is_traversable(
                    candidate_position, existing_node_position):
                # check if this existing node is the one that
                # can be reached the fastest from the candidate
                traversal_time = self._traversal_time(candidate_position,
                                                      existing_node)
                total_time = traversal_time + existing_node.time
                if best_node is None or total_time < best_total_time:
                    best_total_time = total_time
                    best_node = existing_node

        if best_node:
            # generated state can be connected to some existing node
            self._connect_node(best_node, candidate_position)

    def run(self, iterations):
        sg = StateGenerator(*self.view.world_bounds)

        for candidate_position in sg.generate_n(iterations):
            self._connect_to_best(candidate_position)
        self.nodes.sort(key=lambda x: x.time)

    def get_nodes(self):
        return self.nodes


class Arty(Agent):
    SAFETY_THRESHOLD = 0.9  # has no effect in the current implementation

    @property
    def GLOBALMAXEDGE(self):
        return self.radius * 2

    @property
    def LOCALMAXEDGE(self):
        return self.radius * 2

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
                    n.parent.position
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
        else:
            print("No safe route, giving up!")

    def future_position(self, pedestrian, time):
        pos = pedestrian.position + pedestrian.velocity * time
        #pygame.draw.line(self.debugsurface,
        #                 (255, 0, 0),
        #                 pedestrian.position,
        #                 pos)
        return pos

    def safeness_pedestrians(self, position, view, time):
        """Probability that position will be collision free

        At specified time with respect to pedestrians in view
        """
        for p in view.pedestrians:
            # extrapolate position
            pedestrianpos = self.future_position(p, time)
            safe_dist = (self.radius + p.radius + self.FREEMARGIN)
            if position.distance_to(pedestrianpos) < safe_dist:
                self.safeness_fail_pedestrian = p
                return 0  # collision with pedestrian
        return 1

    def turn_safeness(self, position, a1, a2, view, starttime):
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
                self.safeness_fail_pedestrian = p
                return 0
        return 1

    def line_safeness(self, p1, p2, view, starttime):
        """ Free probability for moving from p1 to p2 starting on starttime """
        if p1 == p2:
            return self.safeness_pedestrians(p1, view, starttime)

        safedist2 = (self.radius + self.FREEMARGIN) ** 2

        for o in view.obstacles:
            if line_distance2(o.p1, o.p2, p1, p2) < safedist2:
                return 0

        diff = p2 - p1
        length = diff.length()
        v = diff / length
        resolution = self.radius
        numsegments = int(math.ceil(length / resolution))
        segmentlen = length / numsegments
        timediff = segmentlen / self.speed

        safeness = 1.0
        for i in xrange(numsegments + 1):
            passed_position = p1 + v * i * segmentlen
            passing_time = starttime + i * timediff
            safeness *= self.safeness_pedestrians(
                passed_position, view, passing_time
            )

        return safeness

    def test_move(self, p1, a1, p2, view, starttime):
        """Get from a state (a1, p1) to ((p2-p1).angle(), p2)

        Returns (traversal_time, safeness)
        """
        diff = p2 - p1
        a2 = diff.angle()
        turningtime = abs(angle_diff(a1, a2)) / self.turningspeed
        movetime = diff.length() / self.speed
        safeness = self.turn_safeness(p1, a1, a2, view, starttime)
        safeness *= self.line_safeness(p1, p2, view, starttime + turningtime)
        return ((turningtime + movetime), safeness)

    def getpath(self, view):
        """Use the ART algorithm to get a path to the goal"""
        if self.goal_occupied(view):
            # TODO: choose another point on the global map
            #       that is closer to the goal than self.position
            return
        #first try to find global node by straight line from current position
        testpath, testtime = self.find_globaltree(
            self.position, self.angle, view, start_time=0.0, start_safeness=1.0
        )
        if testpath:
            return testpath
        print "No safe global path - initializing local search"

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

        solution = None
        solution_time = None

        for reachable_node in self.extended_search(states, view):
            #get the best path to the global graph
            #on to the goal from the new node
            gpath, gtime = self.find_globaltree(
                reachable_node.position,
                reachable_node.angle,
                view,
                start_time=reachable_node.time,
                start_safeness=reachable_node.safeness
            )
            if gpath is not None and (
                solution is None or gtime < solution_time
            ):
                path = []
                n = reachable_node
                while n is not None:
                    path.append(n.position)
                    n = n.parent
                path.reverse()

                for gpos in gpath:
                    path.append(gpos)

                solution = path
                solution_time = gtime
        return solution

    def extension_best_parent(self, new_position, nodes, view):
        bestparent = None
        besttime = None
        for test_parent in nodes:
            segment_time, safeness = self.test_move(
                test_parent.position,
                test_parent.angle,
                new_position,
                view,
                test_parent.time
            )
            newprob = test_parent.safeness * safeness
            if newprob < self.SAFETY_THRESHOLD:
                continue
            endtime = test_parent.time + segment_time

            if bestparent is None or endtime < besttime:
                bestparent = test_parent
                besttime = endtime
        return bestparent

    def subdivide_edge(self, startpos, endpos, max_length):
        diff = endpos - startpos
        angle = diff.angle()
        difflen = diff.length()
        div = int(math.ceil(difflen / max_length))
        for d in xrange(1, div + 1):
            yield angle, startpos + diff * d / div

    def extended_search(self, states, view):
        start = Node(self.position, self.angle,
                     parent=None, time=0, safeness=1)
        nodes = [start]

        for nextpos in states.generate_n(self.LOCALMAXSIZE):
            bestparent = self.extension_best_parent(nextpos, nodes, view)

            if bestparent is None:
                continue

            self.debugsurface.line(
                bestparent.position,
                nextpos
            )
            lastnode = bestparent

            for angle, subpos in self.subdivide_edge(
                bestparent.position,
                nextpos,
                self.LOCALMAXEDGE
            ):
                #add new node and subdivisions to new graph
                move_time, move_safeness = self.test_move(
                    lastnode.position,
                    lastnode.angle,
                    subpos,
                    view,
                    lastnode.time
                )
                if move_safeness < self.SAFETY_THRESHOLD:
                    # FIXME: a subdivision of a safe route should also be safe
                    # but sometimes it isn't. Likely floating point issues...
                    #assert False
                    break
                newnode = Node(
                    subpos,
                    angle,
                    parent=lastnode,
                    time=lastnode.time + move_time,
                    safeness=lastnode.safeness * move_safeness
                )
                lastnode = newnode
                nodes.append(newnode)
                yield newnode

    def find_globaltree(self, from_position, from_angle,
                        view, start_time, start_safeness):
        """Tries to reach global tree from position/angle

            Returns (path, time) to get to goal"""

        # best_path = None
        # best_time_to_goal = None

        for global_candidate in self.globalnodes:
            safeness, path, time_to_goal = self.backtrack_via_global(
                global_candidate,
                from_position,
                from_angle,
                view,
                start_time=start_time,
                start_safeness=start_safeness
            )

            if safeness < self.SAFETY_THRESHOLD:
                self.debugsurface.line(
                    from_position,
                    global_candidate.position,
                    "red"
                )
                continue
            # TODO: make optimality/suboptimality an option
            # With global nodes sorted by time to goal,
            # this is a pretty fast heuristic
            return path, time_to_goal
        #     if best_path is None or time_to_goal < best_time_to_goal:
        #         best_path = path
        #         best_time_to_goal = time_to_goal
        return None, None
        # return (best_path, best_time_to_goal)

    def backtrack_via_global(self, global_candidate, from_position,
                             from_angle, view, start_time, start_safeness):
        # get to global node
        move_time, move_safeness = self.test_move(
            from_position,
            from_angle,
            global_candidate.position,
            view,
            start_time
        )
        safeness = start_safeness * move_safeness
        # is that first straight segment safe?
        if safeness < self.SAFETY_THRESHOLD:
            self.debugsurface.line(
                from_position,
                global_candidate.position,
                "red"
            )
            # don't have to return here since loop below will be skipped anyway

        # update node and time to reflect new position/time
        current_node = global_candidate
        current_time = start_time + move_time

        current_angle = (global_candidate.position - from_position).angle()

        # follow global tree to goal, and check for collisions
        path = [current_node.position]

        while current_node.parent and safeness >= self.SAFETY_THRESHOLD:
            self.safeness_fail_pedestrian = None
            move_time, move_safeness = self.test_move(
                current_node.position,
                current_angle,
                current_node.parent.position,
                view,
                current_time
            )
            safeness *= move_safeness
            if safeness < self.SAFETY_THRESHOLD:
                self.debugsurface.line(
                    global_candidate.position,
                    current_node.position,
                    "pink"
                )
                if self.safeness_fail_pedestrian:
                    self.debugsurface.line(
                        current_node.position,
                        self.safeness_fail_pedestrian.position,
                        "pink"
                    )
                    self.debugsurface.circle(
                        self.safeness_fail_pedestrian.position,
                        10,
                        "red",
                        2
                    )

            current_time += move_time
            current_direction = \
                current_node.parent.position - current_node.position
            current_angle = current_direction.angle()
            current_node = current_node.parent
            path.append(current_node.position)
        return safeness, path, current_time

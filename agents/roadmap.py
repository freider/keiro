from keiro.agent import Agent
from keiro import graphbuilder
from keiro import astar
from keiro.geometry import linesegdist2
from keiro.vector2d import Vec2d


class RoadMap(Agent):
    FREEMARGIN = 1

    def __init__(self, parameter, random):
        if parameter is None:
            parameter = 10
        self.random = random
        super(RoadMap, self).__init__(parameter, random=random)
        self.NODES = parameter
        self.cdist = 10000000

    def think(self, dt, view, debugsurface):
        if not self.goal:  # have no goal?
            return
        #debugsurface.fill((255, 0, 0, 100))
        ccourse = False
        last_pos = self.position
        for i in xrange(self.waypoint_len()):
            for pedestrian in view.pedestrians:
                safe_dist2 = (self.radius +
                              pedestrian.radius +
                              self.FREEMARGIN) ** 2
                closest_dist2 = linesegdist2(
                    last_pos,
                    self.waypoint(i).position,
                    pedestrian.position
                )
                if closest_dist2 <= safe_dist2:
                    ccourse = True
                    break
            last_pos = self.waypoint(i).position
            if ccourse:
                break

        gb = graphbuilder.GraphBuilder(self.speed, self.turningspeed)

        safe_distance = self.radius + self.FREEMARGIN  # some margin is nice
        start = gb.node(self.position, self.angle)
        end = gb.node(self.goal, None)

        if graphbuilder.free_path(
            self.position,
            self.goal,
            view,
            safe_distance
        ):
            gb.connect(self.position, self.goal)
        else:
            # using half of the points for global planning
            world_size = self.view.world_bounds[1::2]
            for i in xrange(self.NODES / 2):
                newpos = Vec2d(
                    self.random.random(),
                    self.random.random()
                ) * Vec2d(*world_size)
                for pos in gb.positions():
                    if graphbuilder.free_path(
                        Vec2d(*pos), newpos, view, safe_distance
                    ):
                        gb.connect(pos, newpos)
                        debugsurface.line(pos, newpos, "green")

            # some extra local points (within view range) to handle the crowd
            for i in xrange(self.NODES - self.NODES / 2):
                random_offset = Vec2d(
                    (2 * self.random.random() - 1) * self.view_range,
                    (2 * self.random.random() - 1) * self.view_range
                )
                newpos = self.position + random_offset
                for pos in gb.positions():
                    if graphbuilder.free_path(
                        Vec2d(*pos), newpos, view, safe_distance
                    ):
                        gb.connect(pos, newpos)
                        debugsurface.line(pos, newpos, "green")

            for p in gb.positions():
                debugsurface.circle(p, 2, "black", 0)

        nodes = gb.all_nodes()
        result = astar.shortest_path(start, end, nodes)
        if result.success:
            result.path = [tuple(self.position)]
            for i in result.indices:
                if result.path[-1] != nodes[i].position:
                    result.path.append(nodes[i].position)

        if ccourse is True:
            self.waypoint_clear()

        # replace current waypoints if we have a better path
        # FIXME: self.cdist is not updated to take into account current
        # position which will penalize the current solution over
        # the last unjustly
        if result.success and (self.waypoint_len() == 0 or
                               result.total_cost < self.cdist):
            self.waypoint_clear()
            for p in result.path:
                self.waypoint_push(Vec2d(*p))
            self.cdist = result.total_cost

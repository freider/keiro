from pedestrian import Pedestrian


class Stubborn(Pedestrian):
    def think(self, dt, view, debugsurface):
        if not self.goal:
            return
        self.waypoint_clear()
        self.waypoint_push(self.goal)

    def render(self, screen):
        Pedestrian.render(self, screen)

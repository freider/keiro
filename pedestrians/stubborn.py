from pedestrian import Pedestrian

class Stubborn(Pedestrian):
	def __init__(self):
		Pedestrian.__init__(self)
	
	def think(self, dt, view, debugsurface):
		if not self.goal:
			return
		self.waypoint_clear()
		self.waypoint_push(self.goal)

	def render(self, screen):
		Pedestrian.render(self, screen)

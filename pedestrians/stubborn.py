from pedestrian import Pedestrian

class Stubborn(Pedestrian):
	def __init__(self):
		Unit.__init__(self)
	
	def think(self, dt, view, debugsurface):
		if not self.goal:
			return
		self.waypoint_clear()
		self.waypoint_push(self.goal)

	def render(self, screen):
		Unit.render(self, screen)

from world import *
import math
import random
import graphutils
import graphs

class RandomWalker(Unit):
	step_mean = 20
	view_range = 15
	def __init__(self, position):
		Unit.__init__(self, position, 0)
	def think(self, dt, view):
		if self.waypoint_len() == 0:
			a = random.random()*math.pi*2
			step = random.gauss(self.step_mean, self.step_mean/3)
			self.waypoint_push(self.position + Vec2d(math.cos(a)*step, math.sin(a)*step))
		
		for p in view:
			if (self.waypoint().position - self.position).angle(p.position - self.position) < math.pi/2:
				self.waypoint_clear()

class Stubborn(Unit):
	view_range = 75
	def __init__(self, position, goal):
		Unit.__init__(self, position, (goal-position).angle())
		self.last_view = ()
		self.goal = goal
		self.waypoint_push(goal)
		self.color = (255, 0,0)
	def think(self, dt, view):
		self.last_view = view

	def render(self, screen):
		Unit.render(self, screen)
		pygame.draw.circle(screen, (255, 150, 150), 
			self.position, self.view_range, 1)
		for p in self.last_view:
			pygame.draw.circle(screen, (150, 255, 150),
				p.position, p.radius, 0)
				
class AStarer(Stubborn):
	view_range = 75
	def __init__(self, position, goal):
		Stubborn.__init__(self, position, goal)
		self.goal = goal
		self.last_view = ()
		

	def think(self, dt, view):
		self.last_view = view
		ccourse = False
		last = self.position
		for i in xrange(self.waypoint_len()):
			for o in view:
				if graphs.linesegdist2(last, self.waypoint(i).position,	o.position) <= (self.radius + o.radius)**2:
					ccourse = True
					break
			last = self.waypoint(i).position
			if ccourse: break

		result = graphs.prp_turning(self, self.goal, view)
		
		if ccourse is True:
			self.waypoint_clear()
			
		if result.success is True and (self.waypoint_len() == 0 or result.total_cost < self.cdist):
			self.waypoint_clear()
			for p in result.path:
				self.waypoint_push(Vec2d(*p))
			self.cdist = result.total_cost

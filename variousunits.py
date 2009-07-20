from world import *
import math
import random
import astar
import graphs

class RandomWalker(Unit):
	step_mean = 20
	view_range = 15
	def __init__(self, position):
		Unit.__init__(self, position)
	def think(self, dt, view):
		for p in view:
			if (self.target(0).position - self.position()).angle(p.position() - self.position()) < math.pi/2:
				self.target_clear()
				
		while self.target_len() < 1:
			a = random.random()*math.pi*2
			step = random.gauss(self.step_mean, self.step_mean/3)
			self.target_push(self.target(self.target_len()-1).position + Vec2d(math.cos(a)*step, math.sin(a)*step))

class Stubborn(Unit):
	view_range = 75
	def __init__(self, position, target):
		Unit.__init__(self, position)
		self.last_view = ()
		self.target_push(target)
		
	def think(self, dt, view):
		self.last_view = view

	def render(self, screen):
		Unit.render(self, screen)
		pygame.draw.circle(screen, (255, 150, 150), 
			self.position(), self.view_range, 1)
		for p in self.last_view:
			pygame.draw.circle(screen, (150, 255, 150),
				p.position(), p.radius, 0)
				
class AStarer(Stubborn):
	view_range = 75
	def __init__(self, position, goal):
		Unit.__init__(self, position)
		self.goal = goal
		self.last_view = ()

	def think(self, dt, view):
		self.last_view = view
		start, end = graphs.rand(self, self.goal, view)
		path = astar.shortest_path(start, end)
		self.target_clear()
		if path is not False: 
			for n in path:
				self.target_push(n.data)
				

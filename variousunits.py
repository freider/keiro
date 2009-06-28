from world import *
import math
import random
		
class RandomWalker(Unit):
	step_mean = 20
	view_range = 0
	def __init__(self, position):
		Unit.__init__(self, position)
		self.lastpos = Vec2d(*self.position)
	def think(self, dt, visible_particles):
		if self.target == self.position:
			a = random.random()*math.pi*2
			step = random.gauss(self.step_mean, self.step_mean/3)
			self.target = self.position + Vec2d(math.cos(a)*step, math.sin(a)*step)
			self.lastpos = Vec2d(*self.position)

class Stubborn(Unit):
	def __init__(self, position, goal):
		Unit.__init__(self, position)
		self.goal = goal
	def think(self, dt, visible_particles):
		self.prev_state = visible_particles
		self.target = self.goal
	def renderIllustration(self, screen):
		pygame.draw.line(screen, (140, 140, 255), 
			self.prev_state.me.position, self.prev_state.me.target)
		pygame.draw.circle(screen, (255, 150, 150), 
			self.prev_state.me.position, self.prev_state.view_range, 1)
		for u in self.prev_state.units:
			pygame.draw.circle(screen, (150, 255, 150),
				u.position, u.radius, 0)

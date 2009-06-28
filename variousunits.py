from world import *
import math
import random
"""
class Bouncer(Unit):
	def moveRight(self):
		self.setTarget(vec2d(self.homeworld.size[0], self.pos.y))
	def moveLeft(self):
		self.setTarget(vec2d(0, self.pos.y))
	def think(self):
		if self.pos.x >= self.homeworld.size[0]:
			self.moveLeft()
		elif self.pos.x <= 0:
			self.moveRight()

class SpeedTester(Unit):
	maxspeed = 10
	def __init__(self):
		self.goal = vec2d(110, 10)
		self.place(vec2d(10,10))
	def think(self):
		if self.target != self.goal:
			self.setTarget(self.goal)
			self.starttime = pygame.time.get_ticks()			
		if self.pos == self.target:
			print 100.0*1000/(pygame.time.get_ticks() - self.starttime)
			self.homeworld.removeUnit(self)"""

		
class RandomWalker(Unit):
	step_mean = 20
	def think(self, dt, visible_particles):
		if self.target == self.position:
			a = random.random()*math.pi*2
			step = random.gauss(self.step_mean, self.step_mean/3)
			self.target = self.position + Vec2d(math.cos(a)*step, math.sin(a)*step)

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

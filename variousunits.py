from world import *
import math
import random

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
	MAXSPEED = 10
	def __init__(self):
		self.goal = vec2d(110, 10)
		self.place(vec2d(10,10))
	def think(self):
		if self.target != self.goal:
			self.setTarget(self.goal)
			self.starttime = pygame.time.get_ticks()			
		if self.pos == self.target:
			print 100.0*1000/(pygame.time.get_ticks() - self.starttime)
			self.homeworld.removeUnit(self)

class RandomWalker(Unit):
	STEP = 20
	def think(self):
		if(self.target == self.pos):
			a = random.random()*math.pi*2
			step = random.gauss(self.STEP, self.STEP/2)
			self.setTarget(self.pos + 
				vec2d(math.cos(a)*step,
						math.sin(a)*step))

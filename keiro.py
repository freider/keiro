from world import *
import math
import random

class Bouncer(Unit):
	def moveRight(self):
		self.setTarget(Position(self.homeworld.size[0], self.pos.y))
	def moveLeft(self):
		self.setTarget(Position(0, self.pos.y))
	def think(self):
		if self.pos.x >= self.homeworld.size[0]:
			self.moveLeft()
		elif self.pos.x <= 0:
			self.moveRight()

class SpeedTester(Unit):
	MAXSPEED = 10
	def __init__(self):
		self.goal = Position(110, 10)
		self.place(Position(10,10))
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
			self.setTarget(self.pos + 
				Position(math.cos(a)*type(self).STEP,
						math.sin(a)*type(self).STEP))

if __name__ == "__main__":
	w = World((320, 240))
	for i in xrange(100):
		u = RandomWalker()
		u.place(Position(random.randrange(w.size[0]), random.randrange(w.size[1])))
		w.addUnit(u)
	#w.addUnit(SpeedTester())
	w.run()

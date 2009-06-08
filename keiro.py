from world import *
import math
import random

class Stupid(Unit):
	MAX_STEP_LENGTH = 8
	def __init__(self, homeworld):
		Unit.__init__(self, homeworld)
		self.step = 1
	def think(self):
		if self.pos.x >= self.homeworld.size[0]:
			self.step = -1
		elif self.pos.x <= 0:
			self.step = 1
		self.place(World.Pos(self.pos.x+self.step, self.pos.y))

if __name__ == "__main__":
	w = World()
	Stupid(w);
	w.run()

from world import *
import math
import random

class Stupid(Unit):
	def moveRight(self):
		self.setTarget(Position(self.homeworld.size[0], self.pos.y))
	def moveLeft(self):
		self.setTarget(Position(0, self.pos.y))
	def think(self):
		if self.pos.x >= self.homeworld.size[0]:
			self.moveLeft()
		elif self.pos.x <= 0:
			self.moveRight()

if __name__ == "__main__":
	w = World((320, 240))
	u = Stupid()
	u.place(Position(w.size)*0.5)
	w.addUnit(u)
	u.moveRight()
	w.run()

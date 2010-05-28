import random
import unittest
from fast.physics import Vec2d

class StateGenerator(object):
	"""Generate 2d vectors within supplied rectangle"""
	def __init__(self, minx, maxx, miny, maxy):
		self.minx = minx
		self.maxx = maxx
		self.miny = miny
		self.maxy = maxy
		
	def generate(self):
		posx = self.minx + random.random()*(self.maxx - self.minx)
		posy = self.miny + random.random()*(self.maxy - self.miny)
		return Vec2d(posx, posy)
		
	def generate_n(self, n):
		for i in xrange(n):
			yield self.generate()
			
class PrependedGenerator(StateGenerator):
	"""Allows bias of the generator by prepending the random queue with non-random points"""
	def __init__(self, minx, maxx, miny, maxy):
		super(PrependedGenerator, self).__init__(minx, maxx, miny, maxy)
		self.biaspoints = []
		
	def prepend(self, point):
		self.biaspoints.append(point)
		
	def generate(self):
		if len(self.biaspoints) > 0:
			ret = self.biaspoints[0]
			del self.biaspoints[0]
			return ret
		else:
			return super(PrependedGenerator, self).generate()
		
		
import unittest
class TestGenerators(unittest.TestCase):
	def setUp(self):
		self.minx = 100
		self.maxx = 200
		self.miny = -200
		self.maxy = -100
		self.sg = StateGenerator(100, 200, -200, -100)
		self.pg = PrependedGenerator(100, 200, -200, -100)

	def test_sg(self):
		for pos in self.sg.generate_n(100):
			self.assertTrue(pos.x >= self.minx and pos.x <= self.maxx)
			self.assertTrue(pos.y >= self.miny and pos.y <= self.maxy)
			
	def test_pg(self):
		bias = self.sg.generate()
		self.assertTrue(self.pg.generate() != bias)
		self.pg.prepend(bias)		
		self.assertTrue(self.pg.generate() == bias)
		self.assertTrue(self.pg.generate() != bias)
		bias2 = self.sg.generate()
		self.pg.prepend(bias)
		self.pg.prepend(bias2)
		self.assertTrue(self.pg.generate() == bias and self.pg.generate() == bias2)
		
if __name__ == "__main__":
	unittest.main()
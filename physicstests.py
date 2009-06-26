import unittest
from physics import *
import physics
class Vec2dTest(unittest.TestCase):
	def setUp(self):
		pass
	
	def testAccess(self):
		vec = Vec2d(5,10)
		vec.x, vec.y = 2, 4
		self.assert_(vec.x == 5 and vec.y == 10)
		
	def testOperators(self):
		vec = Vec2d(5, 10)
		self.assert_(vec == Vec2d(5,10))
		
class _particleTest(unittest.TestCase):
	def setUp(self):
		pass
	def testAccess(self):
		"""Particles position cannot be modified by user"""
		w = World()
		Particle = w.create_particle
		p = Particle(0,0)
		p.position = Vec2d(1,2);
		self.assert_(p.position == Vec2d(0,0))
		p.position.x, p.position.y = 5,10
		self.assert_(p.position == Vec2d(0,0) and p.position.x == 0 and p.position.y == 0)
	
	def testCreation(self):
		exception = False
		try:
			p = _particle(0,0)
		except NameError:
			exception = True			
		
if __name__ == "__main__":
	unittest.main()

import unittest
from physics import *

class Vec2dTest(unittest.TestCase):
	def setUp(self):
		pass
	
	def testAccess(self):
		"""Test immutability"""
		vec = Vec2d(5,10)
		vec.x, vec.y = 2, 4
		self.assert_(vec.x == 5 and vec.y == 10)
		
	def testOperators(self):
		"""Operators"""
		vec = Vec2d(5, 10)
		self.assert_(vec == Vec2d(5,10))
		
class ParticleTest(unittest.TestCase):
	def setUp(self):
		pass
	def testAccess(self):
		"""Particles position cannot be modified by user"""
		p = Particle(0,0)
		p.position = Vec2d(1,2);
		self.assert_(p.position == Vec2d(0,0))
		p.position.x, p.position.y = 5,10
		self.assert_(p.position == Vec2d(0,0) and p.position.x == 0 and p.position.y == 0)
		exception = False
		try:
			p.update(1.0)
		except:
			exception = True
		self.assert_(exception)
	
	def testMemory(self):
		"""Deleted particles are removed from the World they are bound to"""
		p = Particle(0,0)
		w = World()
		w.bind(p);
		self.assert_(w.num_particles() == 1)
		del p
		self.assert_(w.num_particles() == 0)
		
		
if __name__ == "__main__":
	unittest.main()

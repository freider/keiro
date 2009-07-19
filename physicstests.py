import unittest
import math
from physics import *

def almost_equal(a, b, epsilon = 0.001):
	return abs(a-b)<epsilon

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
		
	def testMethods(self):
		"""Vector methods"""
		a = Vec2d(1, 0)
		b = Vec2d(0, 1)
		self.assert_(almost_equal(a.angle(b), math.pi/2))
		a = Vec2d(100,100)
		b = Vec2d(0.5, 0)
		self.assert_(almost_equal(a.angle(b), math.pi/4))

class PathTest(unittest.TestCase):
	def setUp(self):
		pass
	def test(self):
		p = Path(Vec2d(0,0))
		self.assert_(p.position() == Vec2d(0,0))
		p.target_push(Vec2d(3,4))
		self.assert_(p.position() == Vec2d(0,0))
		p.progress(2.5)
		self.assert_(p.position() == Vec2d(1.5,2))
		p.target_push(Vec2d(7,7))
		p.progress(5)
		self.assert_(p.position() == Vec2d(5,5.5))
		p.progress(100)
		self.assert_(p.position() == Vec2d(7,7))

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
		
class WorldTest(unittest.TestCase):
	def setUp(self):
		self.world = World()
	def testRange(self):
		p = Particle(1,0)
		q = Particle(3,0)
		self.world.bind(p)
		self.world.bind(q)
		self.assert_(self.world.num_particles() == 2)
		v = self.world.particles_in_range(p, 1)
		self.assert_(len(v) == 0)
		v = self.world.particles_in_range(p, 2)
		self.assert_(len(v) == 1)
		self.assert_(v[0].this == q.this) #same underlying object hopefully
	
if __name__ == "__main__":
	unittest.main()

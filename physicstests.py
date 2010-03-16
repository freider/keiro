import unittest
import math
from fast.physics import *

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

class ParticleTest(unittest.TestCase):
	def setUp(self):
		pass

	def testAccess(self):
		p = Particle(1,2,0.5)
		self.assert_(p.angle == 0.5)
		self.assert_(p.position == Vec2d(1,2))
		self.assert_(p.waypoint_len() == 0)
		p.waypoint_push(Vec2d(10,10))
		self.assert_(p.waypoint(0).position == Vec2d(10,10))
		p.waypoint(0).position = Vec2d(5,5)
		self.assert_(p.waypoint(0).position == Vec2d(10,10))
		
	def testWaypointing(self):
		p = Particle(10,5,0)
		p.speed = 5
		p.turningspeed = math.pi/2
		waypoints = (Vec2d(15,5), Vec2d(10,5), Vec2d(10,10))
		for t in waypoints:
			p.waypoint_push(t)
		self.assert_(p.position == Vec2d(10,5))
		self.assert_(p.angle == 0)
		self.assert_(p.waypoint_len() == 3)
		for i in xrange(3):
			self.assert_(p.waypoint(i).position == waypoints[i])
		p.update(1)
		self.assert_(p.waypoint_len() == 2)
		self.assert_(p.position == Vec2d(15,5))
		self.assert_(p.angle == 0)
		p.update(1)
		self.assert_(abs(abs(p.angle)-abs(math.pi/2)) < 0.001)
		self.assert_(p.position == Vec2d(15,5))
		p.update(1)
		self.assert_(p.position == Vec2d(15,5))
		self.assert_(abs(abs(p.angle) - abs(math.pi)) < 0.001)
		p.update(2)
		self.assert_(p.position == Vec2d(10,5))
		self.assert_(abs(p.angle - math.pi/2) < 0.001)
		self.assert_(p.waypoint_len() == 1)
		p.update(100)
		self.assert_(p.waypoint_len() == 0)
		self.assert_(p.position == Vec2d(10,10))
		self.assert_(abs(p.angle - math.pi/2) < 0.001)
		
	def testMemory(self):
		"""Deleted particles are removed from the World they are bound to"""
		p = Particle(0,0)
		w = World()
		w.bind(p)
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

	def testObstacles(self):
		ls = LineSegment(Vec2d(0,0), Vec2d(1,2))
		self.world.bind(ls)
		self.assert_(len(self.world.get_obstacles()))
		
if __name__ == "__main__":
	unittest.main()

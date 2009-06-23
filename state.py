from numpy import array, dot

class Particle(object):
	def __init__(self, x, y, vx=0, vy=0):
		self._statematrix = array([[x,vx],[y,vy]])
		self._progressmatrix = array([[1.0,0.0],[0.0,1.0]])
		self.maxspeed = 
		self.radius = 
		self.
		
	def __str__(self):
		return "(%f %f) + t*(%f %f)"%(self.x, self.y, self.vx, self.vy)
		
	def progress(self, dt):
		self._progressmatrix[1][0] = dt
		self._statematrix = dot(self._statematrix, self._progressmatrix)
		
	def getx(self):
		return self._statematrix[0][0]
	def setx(self, x):
		self._statematrix[0][0] = x
	x = property(getx, setx, None)
	
	def gety(self):
		return self._statematrix[1][0]
	def sety(self, y):
		self._statematrix[1][0] = y
	y = property(gety, sety, None)
	
	def getvx(self):
		return self._statematrix[0][1]
	def setvx(self, vx):
		self._statematrix[0][1] = vx
	vx = property(getvx, setvx, None)
	
	def getvy(self):
		return self._statematrix[1][1]
	def setvy(self, vy):
		self._statematrix[1][1] = vy
	vy = property(getvy, setvy, None)
	
	
if __name__ == "__main__":
	import unittest
	
	class UnitTestMovementMatrix(unittest.TestCase):
		def setUp(self):
			pass
		
		def testProperties(self):
			s = Particle(1, 2, 3, 4)
			self.assert_(s.x == 1 and s.y == 2 and s.vx == 3 and s.vy == 4)
			s.x, s.y, s.vx, s.vy = 5, 6, 7, 8
			self.assert_(s.x == 5 and s.y == 6 and s.vx == 7 and s.vy == 8)
		
		def testProgress(self):
			s = Particle(0,0,1,2)
			s.progress(1)
			assert(s.x == 1 and s.y == 2 and s.vx == 1 and s.vy == 2)
			print s
			s.progress(1.5)
			print s
			assert(s.x == 2.5 and s.y == 5 and s.vx == 1 and s.vy == 2)
		
	unittest.main()

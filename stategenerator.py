import random

class StateGenerator(object):
	"""Generate 2d vectors within supplied rectangle"""
	def __init__(self, minx, maxx, miny, maxy):
		self.minx = minx
		self.maxx = maxx
		self.miny = miny
		self.maxy = maxy
		
	def generate(self):
		posx = self.minx + random.random()*(self.maxx - self.minx)
		posx = self.miny + random.random()*(self.maxy - self.miny)
		return Vec2d(posx, posy)
		
		
class PrependedGenerator(StateGenerator):
	"""Allows bias of the generator by prepending the random queue with non-random points"""
	def __init__(self, minx, maxx, miny, maxy):
		super(PrependedGenerator, self).__init__(minx, maxx, miny, maxy)
		self.biaspoints = []
		
	def prepend(self, point):
		self.biaspoints.append(point)
		
	def generate(self):
		if len(biasponts) > 0:
			ret = biasponts[0]
			del biasponts[0]
			return ret
		else:
			return super(PrependedGenerator, self).generate()
		
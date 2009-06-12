import math
class Position(object):
	@property
	def x(self): return self.__pos[0]
	@property
	def y(self): return self.__pos[1]
	
	def __init__(self, *args):
		if len(args) == 1:
			args = args[0]
			if isinstance(args, Position):
				self.__pos = args.__pos
			elif isinstance(args, tuple):
				self.__pos = args
			else:
				raise TypeError
		elif len(args) == 2:
			self.__pos=(args[0],args[1])
		else: 
			raise TypeError(args)
	def __str__(self):
		return str(self.__pos);
	def __mul__(self, v):
		return Position(self.x*v, self.y*v)
	def __sub__(self, p):
		return Position(self.x-p.x, self.y-p.y)
	def __add__(self, p):
		return Position(self.x+p.x, self.y+p.y)
	def __eq__(self, p):
		return int(self.x) == int(p.x) and int(self.y) == int(p.y)
	def __neq__(self, p):
		return not self==p 
	def length(self):
		return math.sqrt(self.x*self.x + self.y*self.y)
	def norm(self):
		l = self.length()
		return Position(self.x/l, self.y/l)
	def toIntTuple(self):
		return (int(self.x), int(self.y))


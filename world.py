from vector import vec2d
import time
import random
import pygame
import sys
try:
	from itertools import combinations
except ImportError:
	def combinations(l, n):
		if n != 2: raise Exception('This placeholder only good for n=2')
		for i in range(len(l)):
			for j in range(i+1, len(l)):
				yield l[i], l[j]

class World(object):
	#MAX_FPS = 1000 #max 100 on some systems
	PRINT_FPS = True
	def __init__(self, size):
		self.units = [];
		self.size = size
		self.clock = pygame.time.Clock()
	
	def addUnit(self, init_position, intelligence):
		u = Unit()
		u.setWorld(self)
		self.units.append(u)
	def removeUnit(self, u):
		self.units.remove(u)
	
	def run(self):
		pygame.init()
		self.screen = pygame.display.set_mode(self.size)
		while 1:
			dt = self.clock.tick()/1000.0

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					print "Bye bye"
					return
					
			moveplan = dict()
			#let everyone set targets
			for u in self.units:
				u.think();
				diff = u.target - u.pos
				length = diff.length
				maxlength = u.maxspeed*dt
				if length <= maxlength:
					newpos = vec2d(u.target)
				else:
					newpos = u.pos + diff.normalized()*maxlength
				u.pos = newpos
			
			for us in combinations(self.units, 2):
				u1, u2 = us
				dist = u1.pos.get_distance(u2.pos)-(u1.radius + u2.radius)
				if dist < 0:
					correction = (u2.pos - u1.pos).normalized()*dist/2
					u2.pos -= correction
					u1.pos += correction
			
			if self.PRINT_FPS:
				sys.stdout.write("%f fps           \r"%self.clock.get_fps())
				sys.stdout.flush()
			self.render(self.screen)
			
	def render(self, screen):
		screen.fill((0,0,0))
		for u in self.units:
			u.render(screen)
		pygame.display.flip()
		
class InteractionLayer(object):
	def __init__(self, me, world):
		self.me = me
		self.units = list()
		self.target = me
		
		for u in world.units:
			#visual range logic goes here
			self.units.append(u)

class IntelRegister(type):
	def __new__(cls, name, bases, dct):
		if name != "Intelligence":
			print "Defining %s"%(name)
		return type.__new__(cls, name, bases, dct)
		
class Intelligence(object):
	__metaclass__ = IntelRegister
	def think(self, interaction_layer):
		raise NotImplementedError
		
class Unit(object):
	maxspeed = 50
	radius = 5
	def __init__(self):
		self.place(vec2d(0,0))
		
	def place(self, pos):
		self.pos = self.target = vec2d(pos)
	
	def setTarget(self, target):
		self.target = target
		
	def render(self, screen):
		color = (255, 255, 0)			
		pygame.draw.circle(screen, color, (int(self.pos.x), int(self.pos.y)), self.radius, 1)
		pygame.draw.line(screen, (140, 140, 255), self.pos, self.target) 
		

from vector import vec2d
from copy import deepcopy
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
		self.size = vec2d(size)
		self.clock = pygame.time.Clock()
	
	def addUnit(self, unit):
		self.units.append(unit)
	
	def run(self):
		pygame.init()
		self.screen = pygame.display.set_mode(self.size)
		while 1:
			dt = self.clock.tick()/1000.0
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					print "Bye bye"
					return

			for u in self.units:
				ilayer = InteractionLayer(u, self, view_range = 50)
				u.ai.think(ilayer)
				u.target = ilayer.target
				maxlength = u.maxspeed*dt
				if u.target_distance() <= maxlength:
					newpos = vec2d(u.target) #copy of vector
				else:
					newpos = u.xy + u.target_direction() * maxlength
				u.xy = newpos
			
			#collision detection
			for us in combinations(self.units, 2):
				u1, u2 = us
				dist = u1.xy.get_distance(u2.xy)-(u1.radius + u2.radius)
				if dist < 0:
					correction = (u2.xy - u1.xy).normalized()*dist/2
					u2.xy -= correction
					u1.xy += correction

			if self.PRINT_FPS:
				sys.stdout.write("%f fps           \r"%self.clock.get_fps())
				sys.stdout.flush()
			self.render(self.screen)
			
	def render(self, screen):
		screen.fill((0,0,0))
		for u in self.units:
			u.render(screen)
			u.ai.renderIllustration(screen)
		pygame.display.flip()
		
class InteractionLayer(object):
	def __init__(self, me, world, view_range = None):
		self.me = me
		self.units = []
		self.target = me.target
		self.view_range = view_range
		
		for u in world.units:
			if view_range is None or view_range >= me.xy.get_distance(u.xy):
				self.units.append(u)

class IntelRegister(type):
	register = []
	def __new__(cls, name, bases, dct):
		if name != "Intelligence":
			print "Defining %s"%(name)
		IntelRegister.register.append((name, cls));
		return type.__new__(cls, name, bases, dct)
		
class Intelligence(object):
	__metaclass__ = IntelRegister
	def think(self, interaction_layer):
		pass
	def renderIllustration(self, screen):
		pass

class Particle(object):
	def __init__(self, position = None):
		self.maxspeed = 30
		self.radius = 5
		self.xy = vec2d(0,0) if position is None else vec2d(position)
		self.target = vec2d(self.xy)
	x = property(lambda: xy.x)
	y = property(lambda: xy.y)
	
	def target_direction(self):
		return (self.target - self.xy).normalized()
	def target_distance(self):
		return (self.target - self.xy).get_length()
			
class Unit(Particle):
	def __init__(self, position, ai):
		Particle.__init__(self, position)
		self.ai = ai
		self.color = (255, 255, 0)
		
	def render(self, screen):
		pygame.draw.circle(screen, self.color, 
			self.xy, self.radius, 1)		

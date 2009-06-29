import time
import random
import pygame
import sys
from physics import Vec2d, Particle, World as PhysicsWorld

class World(PhysicsWorld):
	PRINT_FPS = True
	def __init__(self, size):
		PhysicsWorld.__init__(self);
		self.units = [];
		self.size = Vec2d(*size)
		self.clock = pygame.time.Clock()
	
	def addUnit(self, unit):
		self.units.append(unit)
		self.bind(unit);
	
	def run(self):
		pygame.init()
		pygame.display.set_caption("Crowd Navigation")
		self.screen = pygame.display.set_mode(self.size)
		while 1:
			dt = self.clock.tick()/1000.0
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					print "Bye bye"
					return
			
			self.update(dt)
			for u in self.units:
				if u.view_range != 0:
					view = self.particles_in_range(u, u.view_range)
				else:
					view = ()
				u.think(dt, view)
					
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
	def __init__(self, me, world, view_range = None):
		self.units = []
		self.view_range = view_range
		
		for u in world.units:
			if u is not me and (
				view_range is None or view_range**2 >= me.position.distance_to2(u.position)
			):
				self.units.append(u)

class UnitRegister(type):
	register = []
	def __new__(cls, name, bases, dct):
		if name != "Unit":
			print "Defining %s"%(name)
		IntelRegister.register.append((name, cls));
		return type.__new__(cls, name, bases, dct)
		
class Unit(Particle):
	color = (255, 255, 0)
	view_range = 0
	def __init__(self, position):
		Particle.__init__(self, *position)
		self.radius = 5
		self.speed = 30
	
	def think(self, dt, visible_particles):
		pass
		
	def render(self, screen):
		pygame.draw.circle(screen, self.color, 
			self.position, self.radius, 1)
		pygame.draw.line(screen, (100, 100, 250),
			self.position, self.target, 1)

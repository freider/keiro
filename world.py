import time
import random
import pygame
import sys
import math
from physics import Vec2d, Particle, World as PhysicsWorld

class World(PhysicsWorld):
	PRINT_FPS = False
	THINK_RATIO = 1
	def __init__(self, size):
		PhysicsWorld.__init__(self);
		self.units = [];
		self.size = Vec2d(*size)
		self.clock = pygame.time.Clock()
		self.ticker = 0
	
	def addUnit(self, unit):
		self.units.append(unit)
		self.bind(unit);
	
	def trackUnit(self, unit):
		self.tracked_unit = unit
		
	def run(self):
		pygame.init()
		pygame.display.set_caption("Crowd Navigation")
		self.screen = pygame.display.set_mode(self.size)
		
		self.update(0) #so we have no initial collisions
		self.tracked_unit.collisions = 0
		while 1:
			dt = self.clock.tick()/1000.0
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					print "Collision count:",self.tracked_unit.collisions
					return
			
			self.update(dt)
			if self.ticker == 0:
				for u in self.units:
					if u.view_range != 0:
						view = self.particles_in_range(u, u.view_range)
					else:
						view = ()
					u.think(dt, view)
			self.ticker += 1
			if self.ticker == self.THINK_RATIO:
				self.ticker = 0
			
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
	def __init__(self, position, direction = 0):
		Particle.__init__(self, position[0], position[1], direction)
		self.radius = 5
		self.speed = 30
		self.turningspeed = 2*math.pi/3
	
	def think(self, dt, visible_particles):
		pass
		
	def render(self, screen):
		last = self.position()
		for i in xrange(self.target_len()):
			pygame.draw.line(screen, (100, 100, 250), last, self.target(i).position, 1)
			last = self.target(i).position
		
		pygame.draw.circle(screen, self.color, 
			self.position(), self.radius, 1)	
		pygame.draw.line(screen, self.color,
			self.position(), 
			(self.position().x + math.cos(self.angle())*self.radius, self.position().y + math.sin(self.angle())*self.radius))
		

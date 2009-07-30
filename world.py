import time
import random
import pygame
import sys
import math
from physics import Vec2d, Particle, World as PhysicsWorld

class World(PhysicsWorld):
	def __init__(self, size):
		PhysicsWorld.__init__(self);
		self.units = [];
		self.size = Vec2d(*size)
		self.clock = pygame.time.Clock()
		self.RENDER = True
		self.PRINT_FPS = False
		self.timestep = 0.1
		self.iterations = 0
		self.runtime = 0
		self.callbacks = []
			
	def addUnit(self, unit):
		self.units.append(unit)
		self.bind(unit);
	
	def removeunit(self, unit):
		self.units.remove(unit)
		self.unbind(unit)

	def addcallback(self, where):
		self.callbacks.append(where)
		
	def run(self):
		pygame.init()
		pygame.display.set_caption("Crowd Navigation")
		self.screen = pygame.display.set_mode(self.size)
		
		self.update(0) #so we have no initial collisions
		self.runtime = 0
		self.iterations = 0
		
		while 1:
			if self.timestep == 0:
				dt = self.clock.tick()/1000.0
			else:
				self.clock.tick()
				dt = self.timestep
				
			self.runtime += dt
			self.iterations += 1
			
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
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
			if self.RENDER:
				self.render(self.screen)
			for o in self.callbacks:
				o.update(dt)
			
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
	def __init__(self, position, direction):
		Particle.__init__(self, position[0], position[1], direction)
		self.radius = 5
		self.speed = 30
		self.turningspeed = 2*math.pi/3
	
	def think(self, dt, visible_particles):
		pass
		
	def render(self, screen):
		last = self.position
		for i in xrange(self.waypoint_len()):
			pygame.draw.line(screen, (200, 200, 250), last, self.waypoint(i).position, 1)
			last = self.waypoint(i).position
			pygame.draw.line(screen, (250, 100, 100), last, last, 1)
		
		pygame.draw.circle(screen, self.color, 
			self.position, self.radius, 1)	
		pygame.draw.line(screen, self.color,
			self.position, 
			(self.position.x + math.cos(self.angle)*self.radius, self.position.y + math.sin(self.angle)*self.radius))
		

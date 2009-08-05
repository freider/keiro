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
		

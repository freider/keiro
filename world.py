import time
import random
import pygame
import sys
import math
import os

from fast.physics import Vec2d, Particle, World as PhysicsWorld

class World(PhysicsWorld):
	def __init__(self, size, opts):
		PhysicsWorld.__init__(self)
		self.size = Vec2d(*size)		
		self.units = []
		self.obstacles = []

		self.clock = pygame.time.Clock()
		self.timestep = opts.timestep
		self.capture = opts.capture
		self.fps = opts.fps
		
	def add_unit(self, unit):
		self.units.append(unit)
		self.bind(unit)
	
	def remove_unit(self, unit):
		self.units.remove(unit)
		self.unbind(unit)

	def add_obstacle(self, obstacle):
		self.obstacles.append(obstacle)
		self.bind(obstacle)
		
	def remove_obstacle(self, obstacle):
		self.obstacles.remove(obstacle)
		self.unbind(obstacle)
		
	def init(self):
		pygame.init()
		pygame.display.set_caption("Crowd Navigation")
		self._screen = pygame.display.set_mode(map(int, self.size))
		self._time = 0
		self._iterations = 0
		self.update(0) #so we have no initial collisions
	
	def get_time(self):
		return self._time
	
	def advance(self):
		if self.timestep == 0:
			dt = self.clock.tick()/1000.0 #use real time
		else:
			self.clock.tick()
			dt = self.timestep
			
		self._time += dt
		self._iterations += 1
		
		self.update(dt)
		
		for u in self.units:
			if u.view_range != 0:
				view = self.particles_in_range(u, u.view_range)
			else:
				view = ()
			u.think(dt, view)
				
		if self.fps:
			sys.stdout.write("%f fps           \r"%self.clock.get_fps())
			sys.stdout.flush()
			
		self.render(self._screen)
		return dt
			
	def render(self, screen):
		screen.fill((0,0,0))
		for o in self.obstacles:
			o.render(screen)
		for u in self.units:
			u.render(screen)
		pygame.display.flip()
		
		if self.capture is not None:
			frame_filename = os.path.join((self.capture, "capture_%05d.bmp"%self._iterations))
			pygame.image.save(screen, frame_filename)
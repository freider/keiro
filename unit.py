import pygame
import math
from functools import wraps
from fast.physics import Particle

class Unit(Particle):
	color = (255,255,255)
	view_range = 0
	
	def __init__(self):
		Particle.__init__(self)
		self.radius = 8
		self.speed = 30
		self.turningspeed = 2*math.pi/3
		self.iteration_listeners = []
			
	def add_iteration_listener(self, listener):
		self.iteration_listeners.append(listener)
			
	def think(self, dt, view, debugsurface):
		pass
		
	def render(self, screen):
		pygame.draw.circle(screen, self.color, 
			map(int, self.position), int(self.radius), 0)
		pygame.draw.circle(screen, (0,0,0), 
			map(int, self.position), int(self.radius), 2)
			
		#this draws a direction vector for a unit
		dirvector = map(int, (self.position.x + math.cos(self.angle)*self.radius, self.position.y + math.sin(self.angle)*self.radius))
		
		pygame.draw.line(screen, (0,0,0),
			map(int, self.position), 
			dirvector, 2)
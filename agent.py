import math
import random
import pygame
from functools import wraps
from fast.physics import Vec2d
from unit import Unit

def iteration(f):
	"""Do not inherit the anything wrapped, or the iteration will only cover the inherited code..."""
	@wraps(f)
	def wrapper(self, *args):
		for il in self.iteration_listeners:
			il.start_iteration()
		f(self, *args)
		for il in self.iteration_listeners:
			il.end_iteration()
		
	return wrapper

class AgentRegistrar(type):
	register = {}
	def __new__(cls, name, bases, dct):
		ret = AgentRegistrar.register[name] = type.__new__(cls, name, bases, dct)
		return ret

class Agent(Unit):
	"""Base class for all navigational algorithms"""
	__metaclass__ = AgentRegistrar
	
	view_range = 100
	def __init__(self):
		super(Agent, self).__init__()
		self.color = (100, 100,255)

	def render(self, screen):
		#draw a cross over the target
		pygame.draw.aaline(screen, (255, 0, 0),
				self.goal + Vec2d(-10,-10), self.goal + Vec2d(10,10))
		pygame.draw.aaline(screen, (255, 0, 0),
				self.goal + Vec2d(10,-10), self.goal + Vec2d(-10,10))
				
		super(Agent, self).render(screen)
		#pygame.draw.circle(screen, self.color, 
		#	map(int, self.position), int(self.radius), 0)
		
		#draw all waypoints
		last = self.position
		for i in xrange(self.waypoint_len()):
			pygame.draw.aaline(screen, (0, 0, 0), last, self.waypoint(i).position)
			last = self.waypoint(i).position
			pygame.draw.aaline(screen, (0, 0, 0), last, last)
			
		#draw viewrange
		pygame.draw.circle(screen, (100, 100, 100), 
			map(int, self.position), int(self.view_range), 1)
	
	def init(self, view):
		"""Called before simulation starts with the initial information available to the agent"""
		pass
	
	@iteration	
	def think():
		pass
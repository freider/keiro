from world import *
import math
import random
from fast import graphutils, physics
import graphs
from functools import wraps

def iteration(f):
	@wraps(f)
	def wrapper(self, dt, view):
		for il in self.iteration_listeners:
			il.start_iteration()
		f(self, dt, view)
		for il in self.iteration_listeners:
			il.end_iteration()
		self.last_view = view
		
	return wrapper
	
class UnitRegistrar(type):
	register = {}
	def __new__(cls, name, bases, dct):
		ret = UnitRegistrar.register[name] = type.__new__(cls, name, bases, dct)
		return ret
		
class Unit(Particle):
	__metaclass__ = UnitRegistrar

	color = (100, 100, 0)
	view_range = 0
	
	def __init__(self):
		Particle.__init__(self)
		self.radius = 5
		self.speed = 30
		self.turningspeed = 2*math.pi/3
		self.iteration_listeners = []
	
	def add_iteration_listener(self, listener):
		self.iteration_listeners.append(listener)
			
	def think(self, dt, view):
		pass
		
	def render(self, screen):
		pygame.draw.circle(screen, self.color, 
			map(int, self.position), int(self.radius), 1)
			
		#this draws a direction vector for a unit
		pygame.draw.aaline(screen, self.color,
			map(int, self.position), 
			map(int, (self.position.x + math.cos(self.angle)*self.radius, self.position.y + math.sin(self.angle)*self.radius)))
			
class RandomWalker(Unit):
	step_mean = 20
	view_range = 15
	def __init__(self):
		Unit.__init__(self)
	def think(self, dt, view):		
		if self.waypoint_len() == 0:
			a = random.random()*math.pi*2
			step = random.gauss(self.step_mean, self.step_mean/3)
			self.waypoint_push(self.position + Vec2d(math.cos(a)*step, math.sin(a)*step))
		
		direction = self.waypoint().position - self.position
		for p in view.pedestrians: #stop if any pedestrians in 
			if direction.angle(p.position - self.position) < math.pi/2:
				self.waypoint_clear()
				return
		
		for o in view.obstacles: #avoid obstacles
			if graphs.line_distance2(self.position, self.waypoint().position, o.p1, o.p2) <= self.radius**2:
				self.waypoint_clear()
				return

class Stubborn(Unit):
	def __init__(self):
		Unit.__init__(self)
	
	def think(self, dt, view):
		if not self.goal:
			return
		self.waypoint_clear()
		self.waypoint_push(self.goal)

	def render(self, screen):
		Unit.render(self, screen)

class Agent(Unit):
	"""Same as unit, but with some prettier renderings"""
	def __init__(self):
		super(Agent, self).__init__()
		self.color = (200, 50,50)

	def render(self, screen):
		#draw a cross over the target
		pygame.draw.aaline(screen, (255, 0, 0),
				self.goal + Vec2d(-10,-10), self.goal + Vec2d(10,10))
		pygame.draw.aaline(screen, (255, 0, 0),
				self.goal + Vec2d(10,-10), self.goal + Vec2d(-10,10))
				
		#super(Agent, self).render(screen)
		pygame.draw.circle(screen, self.color, 
			map(int, self.position), int(self.radius), 0)
		
		#draw all waypoints
		last = self.position
		for i in xrange(self.waypoint_len()):
			pygame.draw.aaline(screen, (100, 100, 150), last, self.waypoint(i).position)
			last = self.waypoint(i).position
			pygame.draw.aaline(screen, (150, 50, 50), last, last)
			
		#draw viewrange
		pygame.draw.circle(screen, (150, 150, 150), 
			map(int, self.position), int(self.view_range), 1)

		#mark pedestrians in view range
		for p in self.last_view.pedestrians:
			pygame.draw.circle(screen, (100, 200, 100),
				map(int, p.position), int(p.radius), 0)
	
	@iteration	
	def think():
		pass
		
class AStarer(Agent):
	view_range = 75
	def __init__(self):
		super(AStarer, self).__init__()
		self.cdist = 10000000
	
	@iteration	
	def think(self, dt, view):		
		if not self.goal:
			return
		ccourse = False
		last = self.position
		for i in xrange(self.waypoint_len()):
			for o in view.pedestrians:
				if graphs.linesegdist2(last, self.waypoint(i).position,	o.position) <= (self.radius + o.radius)**2:
					ccourse = True
					break
			last = self.waypoint(i).position
			if ccourse: break

		result = graphs.random_roadmap(self, self.goal, view, graphs.GraphBuilder(self.speed, self.turningspeed))
	
		if ccourse is True:
			self.waypoint_clear()
			
		if result.success is True and (self.waypoint_len() == 0 or result.total_cost < self.cdist):
			self.waypoint_clear()
			for p in result.path:
				self.waypoint_push(Vec2d(*p))
			self.cdist = result.total_cost
	

class Arty(AStarer):
	view_range = 75
	def __init__(self):
		super(Arty, self).__init__()
	
	@iteration	
	def think(self, dt, view):
		if not self.goal:
			return
		path = graphs.ARTBuilder().build(self, self.goal, view, 100)
		self.waypoint_clear()
		if path is not False:
			for p in path:
				self.waypoint_push(p)
from world import *
import math
import random
from fast import graphutils, physics
import graphs
from functools import wraps
import pygame


def iteration(f):
	"""Do not inherit the anything wrapped, or the iteration will only cover the inherited code..."""
	@wraps(f)
	def wrapper(self, dt, view, debugsurface):
		for il in self.iteration_listeners:
			il.start_iteration()
		f(self, dt, view, debugsurface)
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
		self.radius = 8
		self.speed = 30
		self.turningspeed = 2*math.pi/3
		self.iteration_listeners = []
	
	def add_iteration_listener(self, listener):
		self.iteration_listeners.append(listener)
			
	def think(self, dt, view, debugsurface):
		pass
		
	def render(self, screen):
		pygame.draw.circle(screen, (255,255,255), 
			map(int, self.position), int(self.radius), 0)
		pygame.draw.circle(screen, self.color, 
			map(int, self.position), int(self.radius), 2)
			
		#this draws a direction vector for a unit
		pygame.draw.aaline(screen, self.color,
			map(int, self.position), 
			map(int, (self.position.x + math.cos(self.angle)*self.radius, self.position.y + math.sin(self.angle)*self.radius)))
			
class RandomWalker(Unit):
	step_mean = 20
	view_range = 25
	def __init__(self):
		Unit.__init__(self)
	def think(self, dt, view, debugsurface):		
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
	
	def think(self, dt, view, debugsurface):
		if not self.goal:
			return
		self.waypoint_clear()
		self.waypoint_push(self.goal)

	def render(self, screen):
		Unit.render(self, screen)

class Agent(Unit):
	view_range = 100
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
			pygame.draw.aaline(screen, (0, 0, 0), last, self.waypoint(i).position)
			last = self.waypoint(i).position
			pygame.draw.aaline(screen, (0, 0, 0), last, last)
			
		#draw viewrange
		pygame.draw.circle(screen, (100, 100, 100), 
			map(int, self.position), int(self.view_range), 1)

		#mark pedestrians in view range
		for p in self.last_view.pedestrians:
			pygame.draw.circle(screen, (100, 200, 100),
				map(int, p.position), int(p.radius), 0)
	
	@iteration	
	def think():
		pass
		
class RoadMap(Agent):
	def __init__(self):
		super(RoadMap, self).__init__()
		self.cdist = 10000000
	
	@iteration	
	def think(self, dt, view, debugsurface):		
		if not self.goal: #have no goal?
			return
		#debugsurface.fill((255, 0, 0, 100))
		ccourse = False
		last = self.position
		for i in xrange(self.waypoint_len()):
			for o in view.pedestrians:
				if graphs.linesegdist2(last, self.waypoint(i).position,	o.position) <= (self.radius + o.radius)**2:
					ccourse = True
					break
			last = self.waypoint(i).position
			if ccourse: break

		graphbuilder = graphs.GraphBuilder(self.speed, self.turningspeed)
		
		safe_distance = self.radius+1 #some margin is nice
		start = graphbuilder.node(self.position, self.angle)
		end = graphbuilder.node(self.goal, None)

		if graphs.free_path(self.position, self.goal, view, safe_distance):
			graphbuilder.connect(self.position, self.goal)
		else:
			for i in xrange(10): #global planning
				newpos = Vec2d(640*random.random(), 480*random.random())
				for pos in graphbuilder.positions():
					if graphs.free_path(Vec2d(*pos), newpos, view, safe_distance):
						graphbuilder.connect(pos, newpos)

			for i in xrange(10): #some extra local points to handle the crowd
				newpos = self.position + Vec2d((2*random.random()-1)*self.view_range, (2*random.random()-1)*self.view_range)
				for pos in graphbuilder.positions():
					if graphs.free_path(Vec2d(*pos), newpos, view, safe_distance):
						graphbuilder.connect(pos, newpos)
						pygame.draw.aaline(debugsurface, (0,255,0,255), pos, newpos)
						
			for p in graphbuilder.positions():
				pygame.draw.circle(debugsurface, (0,0,0), p, 2, 0)

		nodes = graphbuilder.all_nodes()
		result = graphutils.shortest_path(start, end, nodes)
		if result.success:
			result.path = [tuple(self.position)]
			for i in result.indices:
				if result.path[-1] != nodes[i].position:
					result.path.append(nodes[i].position)
		
	
		if ccourse is True:
			self.waypoint_clear()
			
		if result.success is True and (self.waypoint_len() == 0 or result.total_cost < self.cdist):
			self.waypoint_clear()
			for p in result.path:
				self.waypoint_push(Vec2d(*p))
			self.cdist = result.total_cost
	
class RandomTree(Agent):
	def __init__(self):
		super(RandomTree, self).__init__()
		
	@iteration
	def think(self, dt, view, debugsurface):
		pass
		
class Arty(Agent):
	def __init__(self):
		super(Arty, self).__init__()
	
	@iteration	
	def think(self, dt, view, debugsurface):
		if not self.goal:
			return
		path = graphs.ARTBuilder(debugsurface).build(self, self.goal, view, 500)
		self.waypoint_clear()
		if path:
			for p in path:
				self.waypoint_push(p)
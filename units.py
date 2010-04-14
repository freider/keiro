from world import *
import math
import random
from fast import graphutils, physics
from fast.physics import Vec2d, linesegdist2, line_distance2, angle_diff

import graphs
from functools import wraps
import pygame


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
	
class UnitRegistrar(type):
	register = {}
	def __new__(cls, name, bases, dct):
		ret = UnitRegistrar.register[name] = type.__new__(cls, name, bases, dct)
		return ret
		
class Unit(Particle):
	__metaclass__ = UnitRegistrar

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
						pygame.draw.aaline(debugsurface, (0,255,0,255), pos, newpos)

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
	SAFETY_THRESHOLD = 0.9
	GLOBALNODES = 300
	GLOBALMINEDGE = 50
	class Node:
		def __init__(self, position, angle, parent, time = None, freeprob = None):
			self.position = position
			self.angle = angle
			self.time = time
			self.parent = parent
			self.freeprob = freeprob
			
	def __init__(self):
		super(Arty, self).__init__()
	
	def init(self, view):
		"""Builds the static obstacle map, global roadmap"""
		#RRT from goal
		nodes = [self.Node(self.goal, None, None)]
		for i in xrange(self.GLOBALNODES):
			newpos = Vec2d(random.randrange(640), random.randrange(480)) #TODO: remove hardcoded world size
			besttime = None
			bestnode = None
			for tonode in nodes:
				topos = tonode.position
				connectable = True
				for o in view.obstacles:
					if line_distance2(topos, newpos, o.p1, o.p2) <= self.radius:
						connectable = False
						break
						
				if connectable:
					dist = topos.distance_to(newpos)
					if tonode.parent is None:
						turndist = 0 #goal node
					else:
						turndist = abs(angle_diff((topos - newpos).angle(), tonode.angle))
					time = dist/self.speed + turndist/self.turningspeed
					
					if bestnode is None or time < besttime:
						besttime = time
						bestnode = tonode
			if bestnode:
				topos = bestnode.position
				diff = topos - newpos
				angle = diff.angle()
				vdir = diff.norm()
				difflen = diff.length()
				div = 1
				while difflen/div > self.GLOBALMINEDGE:
					div += 1
				#subdivide the new edge
				for d in xrange(div):
					nodes.append(self.Node(newpos + vdir*d*difflen/div, angle, bestnode))
		self.globalnodes = nodes
		print "Done building global RRT"		
		
	def freeprob(self, position, view, time):
		"""Returns probability that specified position will be collision free at specified time"""
		POSITIVE = 1
		NEGATIVE = 0
		
		for o in view.obstacles:
			if linesegdist2(o.p1, o.p2, position) <= self.radius**2:
				return 0 #collision with static obstacle
				
		for p in view.pedestrians:
 			pedestrianpos = p.position + p.velocity*time #extrapolated position
			if position.distance_to(pedestrianpos) < (self.radius + p.radius):
				return NEGATIVE
		return POSITIVE
	
	def path_eta(self, path, view):
		"""Returns ETA for the current plan.

		Assumes static obstacles don't change"""
		if not (path[0] == self.position and path[-1] == self.goal):
			return None #must go between current position and goal
		ctime = 0
		freeprob = 1.0
		a1 = self.angle
		p1 = self.position

		for p2 in path[1:]:
			a2 = (p2 - p1).angle()
			ctime += abs(angle_diff(a1, a2))/self.turningspeed + p1.distance_to(p2)/self.speed
			p1 = p2
			a1 = a2
			freeprob *= self.freeprob(p2, view, ctime)
			if freeprob < self.SAFETY_THRESHOLD:
				return None
				
		return ctime
			
	def getpath(self, max_size):
		start = Arty.Node(self.position, self.angle, parent = None, time = 0, freeprob = 1)
		
		if self._freeprob(self.position, self.angle, self.goal, 0)[0] > self.SAFETY_THRESHOLD:
			return [self.position, self.goal] #direct path

		nodes = [start]
		
		#always use the nodes from the last solution in this iterations so they are kept if still good enough
		#TODO: if using last path, check if a better one can be found to refine previous bad paths
		
		trypos = [self.waypoint(i).position for i in xrange(self.waypoint_len())]
		while len(trypos) < max_size: 
			trypos.append(Vec2d(random.random()*640, random.random()*480)) #FIXME: hardcoded world dimensions

		for nextpos in trypos:
			best = None
			for n in nodes:
				frompos = n.position
				freeprob, endtime = self._freeprob(frompos, n.angle, nextpos, n.time)
				newprob = freeprob * n.freeprob
				#if newprob > self.SAFETY_THRESHOLD:
				if best is None or best[1] > endtime:
					best = (newprob, endtime, n)

			if best is not None:
				newprob, new_time, parent = best[0], best[1], best[2]
				if newprob < self.SAFETY_THRESHOLD:
					#don't add paths below the safety threshold
					pygame.draw.line(self.debugsurface, (255,0,0), parent.position, nextpos)
					continue
				else:
					pygame.draw.line(self.debugsurface, (0,255,0), parent.position, nextpos)

				newnode = Arty.Node(nextpos, (nextpos - n.position).angle(), parent = parent, time = new_time, freeprob = newprob)
				nodes.append(newnode)

				#always check if the new node has a good enough path to the goal
				freeprob, endtime = self._freeprob(newnode.position, newnode.angle, self.goal, new_time)
				target_prob = freeprob*newprob
				
				if target_prob > self.SAFETY_THRESHOLD:
					path = [self.goal]
					n = newnode
					while n != None:
						path.append(n.position)
						n = n.parent
					path.reverse()
					return path
		
	@iteration	
	def think(self, dt, view, debugsurface):
		if not self.goal:
			return
		self.view = view
		self.debugsurface = debugsurface
		#for n in self.globalnodes:
		#	if n.parent:
		#		pygame.draw.line(debugsurface, pygame.Color("black"), n.position, n.parent.position)
		#		pygame.draw.circle(debugsurface, pygame.Color("red"), n.position, 2, 0)
		path = self.getpath(500)
		self.waypoint_clear()
		
		if path:
			for p in path:
				self.waypoint_push(p)

import unittest
class TestPathETA(unittest.TestCase):
	def setUp(self):
		a = Arty()
		a.position = Vec2d(1,0)
		a.angle = 0
		a.speed = 1
		a.goal = Vec2d(3,0)
		self.a = a

	def test_success(self):
		a = self.a
		a.angle = 0
		a.turningspeed = math.pi/2
		path = [a.position, Vec2d(1,1), a.position, a.goal]
		res = a.path_eta(path, View([],[]))
		self.assertFalse(res is None)
		self.assertAlmostEqual(res, 8, places = 5)
		a.angle = math.pi/2
		res = a.path_eta(path, View([],[]))
		self.assertFalse(res is None)
		self.assertAlmostEqual(res, 7, places = 5)
		a.angle = -math.pi/4
		res = a.path_eta(path, View([],[]))
		self.assertFalse(res is None)
		self.assertAlmostEqual(res, 8.5, places = 5)
		a.angle = -math.pi*3/4
		res = a.path_eta(path, View([],[]))
		self.assertFalse(res is None)
		self.assertAlmostEqual(res, 8.5, places = 5)
		
	def test_fail_pedestrian(self):
		a = self.a
		path = [a.position, a.goal]
		p = Unit()
		p.position = Vec2d(1,0)
		view = View([], [p])
		res = a.path_eta(path, view)
		self.assertTrue(res is None)
		
	def test_fail_wall(self):
		import obstacle
		a = self.a
		path = [a.position, a.goal]
		o = obstacle.Line(Vec2d(2,1), Vec2d(2,-1))
		view = View(o.bounds, [])
		res = a.path_eta(path, view)
		self.assertTrue(res is None)
		
if __name__ == "__main__":
	unittest.main()
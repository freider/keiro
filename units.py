from world import *
import math
import random
from fast import graphutils, physics
from fast.physics import Vec2d, linesegdist2, line_distance2, angle_diff
from stategenerator import PrependedGenerator
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
	step_mean = 200
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
	GLOBALNODES = 30
	GLOBALMINEDGE = 50
	LOCALMINEDGE = 50
	LOCALMAXSIZE = 50
	
	class Node:
		def __init__(self, position, angle, parent, time = None, freeprob = None):
			self.position = position
			self.angle = angle
			self.time = time
			self.parent = parent
			self.freeprob = freeprob
			
	def __init__(self):
		super(Arty, self).__init__()
	
	def globaltree(self, view):
		#RRT from goal
		nodes = [self.Node(self.goal, None, None)]
		while len(nodes) < self.GLOBALNODES:
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
				diff = newpos - topos
				angle = diff.angle()
				vdir = diff.norm()
				difflen = diff.length()
				div = int(math.ceil(difflen/self.GLOBALMINEDGE))
				prev = bestnode
				#subdivide the new edge
				for d in xrange(1, div+1):
					newnode = self.Node(topos + diff*d/div, angle, prev)
					nodes.append(newnode)
					prev = newnode
		
		#DEBUG
		# poss = []
		# 		for n in nodes:
		# 			poss.append((n.position[0], n.position[1]))
		# 		poss.sort()
		# 		for p in poss:
		# 			print p
		
		self.globalnodes = nodes
		print "Done building global RRT", len(self.globalnodes)
		
	def init(self, view):
		"""Builds the static obstacle map, global roadmap"""
		self.globaltree(view)
		
	def freeprob(self, position, view, time):
		"""Returns probability that specified position will be collision free at specified time"""
		for o in view.obstacles:
			if linesegdist2(o.p1, o.p2, position) <= self.radius**2:
				return 0 #collision with static obstacle
				
		for p in view.pedestrians:
 			pedestrianpos = p.position + p.velocity*time #extrapolated position
			if position.distance_to(pedestrianpos) < (self.radius + p.radius):
				return 0 #collision with pedestrian
		return 1
	
	def freeprob_turn(self, position, a1, a2, view, starttime):
		dur = angle_diff(a1, a2)/self.turningspeed
		for p in view.pedestrians:
			p1 = p.position
			p2 = p1 + p.velocity*dur #extrapolate
			if linesegdist2(p1, p2, position) < (self.radius + p.radius)**2:
				return 0	
		return 1
	
	def freeprob_line(self, p1, p2, view, starttime):
		if p1 == p2:
			return self.freeprob(p1, view, starttime)
			
		diff = p2 - p1
		length = diff.length()
		v = diff/length
		resolution = self.radius
		numsegments = int(math.ceil(length/resolution))
		segmentlen = length/numsegments
		timediff = segmentlen/self.speed
		
		freeprob = 1.0
		for i in xrange(numsegments+1):
			freeprob *= self.freeprob(p1 + v*i*segmentlen, view, starttime + i*timediff)
		
		return freeprob
	
	def freeprob_turn_line(self, p1, a1, p2, view, starttime):
		"""Free probability for turning and then walking on a straight line"""
		a2 = (p2-p1).angle()
		dt = abs(angle_diff(a1, a2))/self.turningspeed
		free = self.freeprob_turn(p1, a1, a2, view, starttime)
		free *= self.freeprob_line(p1, p2, view, starttime + dt)
		return free
		
	def path_valid(self, path, view):
		"""Returns if a path is safe (i.e. deemed collision free)"""
		ctime = 0
		freeprob = 1.0
		a1 = self.angle
		p1 = self.position

		for p2 in path[1:]:
			a2 = (p2 - p1).angle()
			freeprob *= self.freeprob_turn_line(p1, a1, p2, view, ctime)
			ctime += abs(angle_diff(a1, a2))/self.turningspeed + p1.distance_to(p2)/self.speed
			p1 = p2
			a1 = a2
			if freeprob < self.SAFETY_THRESHOLD:
				return False	
		return True
		
	def segment_time(self, a1, p1, p2):
		"""Returns time to get from a state (a1, p1) to ((p2-p1).angle(), p2)"""
		diff = p2 - p1
		turningtime = abs(angle_diff(a1, diff.angle()))/self.turningspeed
		movetime = diff.length()/self.speed
		return turningtime + movetime
		
	def path_time(self, path, startangle = None):
		"""Returns the time it would take to traverse a path assuming there are no collisions"""
		if startangle is None:
			startangle = self.angle
		a1 = startangle
		p1 = path[0]
		tottime = 0
		for p2 in path[1:]:
			tottime += self.segment_time(a1, p1, p2)
			a1 = (p2 - p1).angle()
			p1 = p2
		return tottime
			
	def getpath(self, view):
		"""Use the Art algorithm to get a path to the goal"""
		
		#first try to find global node by local planner from current position
		testpath, testtime = self.find_globaltree(self.position, self.angle, view, 0, 1)
		if testpath:
			return testpath
		print "Cannot find global path from current, extending search tree"
		
		start = Arty.Node(self.position, self.angle, parent = None, time = 0, freeprob = 1)
		nodes = [start]

		states = PrependedGenerator(self.position.x - self.view_range, self.position.x + self.view_range,
									self.position.y - self.view_range, self.position.y + self.view_range)
		
		#always try to use the nodes from the last solution in this iterations so they are kept if still the best
		for i in xrange(self.waypoint_len()):
			pos = self.waypoint(i).position
			if pos.distance_to(self.position) <= self.radius:
				states.prepend(pos)
			
		for nextpos in states.generate_n(self.LOCALMAXSIZE):
			bestparent = None
			for n in nodes:
				freeprob = self.freeprob_turn_line(n.position, n.angle, nextpos, view, n.time)
				endtime = n.time + self.segment_time(n.angle, n.position, nextpos)
				
				newprob = freeprob * n.freeprob
				if newprob < self.SAFETY_THRESHOLD:
					continue
				if bestparent is None or besttime > endtime:
					bestparent = n
					besttime = endtime

			if bestparent is not None:
				pygame.draw.line(self.debugsurface, (0,255,0), bestparent.position, nextpos)
				#subdivide the new edge
				diff = nextpos - bestparent.position
				angle = diff.angle()
				difflen = diff.length()
				vdir = diff/difflen
				div = int(math.ceil(difflen/self.LOCALMINEDGE))
				
				lastnode = bestparent
				
				for d in xrange(1, div+1):
					#not 100% sure everything here is correct, variable names are a bit confusing...
					subpos = bestparent.position + diff*d/div
					freeprob = self.freeprob_turn_line(lastnode.position, lastnode.angle, subpos, view, lastnode.time)
					dt = self.segment_time(lastnode.angle, lastnode.position, subpos)
					newnode = self.Node(subpos, angle, parent = lastnode, time = lastnode.time + dt, freeprob = lastnode.freeprob * freeprob)
					lastnode = newnode
					nodes.append(newnode)

					#get the best path to the global graph on to the goal from the new node
					gpath, gtime = self.find_globaltree(newnode.position, newnode.angle, view, newnode.time, newnode.freeprob)
					
					if gpath is not None:
						path = []
						n = newnode
						while n != None:
							path.append(n.position)
							n = n.parent
						path.reverse()
						
						for gpos in gpath:
							path.append(gpos)
						return path
	
	def find_globaltree(self, p1, a1, view, time, startprob):
		"""Tries to reach global tree from position/angle
		
			Returns (path, time) to get to goal"""
			
		bestpath = None
		besttime = None
	
		for n in self.globalnodes:
			a2 = (n.position - p1).angle()
			free = startprob * self.freeprob_turn(p1, a1, a2, view, time)
			time += abs(angle_diff(a1, a2))/self.turningspeed
			free *= self.freeprob_turn_line(p1, a1, n.position, view, time)
			
			if free >= self.SAFETY_THRESHOLD:
				#try to reach goal from global node
				path = []
				cur = n
				while cur.parent != None:
					path.append(cur.position)
					free *= self.freeprob_turn_line(cur.position, cur.angle, cur.parent.position, view, time)
					time += self.segment_time(cur.angle, cur.position, cur.parent.position)
					cur = cur.parent
					
				path.append(cur.position)
				
				if bestpath is None or time < besttime:
					bestpath = path
					besttime = time
					
		return (bestpath, besttime)
			
			
	@iteration	
	def think(self, dt, view, debugsurface):
		if not self.goal:
			return
		self.view = view
		self.debugsurface = debugsurface
		for n in self.globalnodes:
			if n.parent:
				pygame.draw.line(debugsurface, pygame.Color("black"), n.position, n.parent.position)
			pygame.draw.circle(debugsurface, pygame.Color("red"), n.position, 2, 0)

		path = self.getpath(view)
		self.waypoint_clear()
		
		if path:
			for p in path:
				self.waypoint_push(p)

import unittest
class TestPathTime(unittest.TestCase):
	def setUp(self):
		a = Arty()
		a.position = Vec2d(1,0)
		a.angle = 0
		a.speed = 1
		a.goal = Vec2d(3,0)
		a.turningspeed = math.pi/2
		self.path = [a.position, Vec2d(1,1), a.position, a.goal]
		self.a = a

	def test_1(self):
		self.a.angle = 0
		res = self.a.path_time(self.path)
		self.assertAlmostEqual(res, 8, places = 5)
		
	def test_2(self):
		res = self.a.path_time(self.path, math.pi/2)
		self.assertAlmostEqual(res, 7, places = 5)
		
	def test_3(self):	
		self.a.angle = -math.pi/4
		res = self.a.path_time(self.path)
		self.assertAlmostEqual(res, 8.5, places = 5)

	def test_4(self):
		self.a.angle = -math.pi*3/4
		res = self.a.path_time(self.path)
		self.assertAlmostEqual(res, 8.5, places = 5)
		
	def _test_fail_pedestrian(self):
		a = self.a
		path = [a.position, a.goal]
		p = Unit()
		p.position = Vec2d(1,0)
		view = View([], [p])
		res = a.path_time(path, view)
		self.assertTrue(res is None)
		
	def _test_fail_wall(self):
		import obstacle
		a = self.a
		path = [a.position, a.goal]
		o = obstacle.Line(Vec2d(2,1), Vec2d(2,-1))
		view = View(o.bounds, [])
		res = a.path_time(path, view)
		self.assertTrue(res is None)

if __name__ == "__main__":
	unittest.main()
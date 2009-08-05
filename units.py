from world import *
import math
import random
import graphutils
import graphs
import physics

class UnitRegistrar(type):
	register = {}
	def __new__(cls, name, bases, dct):
		if name != "Unit":
			print "Defining unit %s"%(name,)
		ret = UnitRegistrar.register[name] = type.__new__(cls, name, bases, dct)
		return ret
		
class Unit(Particle):
	__metaclass__ = UnitRegistrar
	
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

class RandomWalker(Unit):
	step_mean = 20
	view_range = 15
	def __init__(self, position):
		Unit.__init__(self, position, 0)
	def think(self, dt, view):
		if self.waypoint_len() == 0:
			a = random.random()*math.pi*2
			step = random.gauss(self.step_mean, self.step_mean/3)
			self.waypoint_push(self.position + Vec2d(math.cos(a)*step, math.sin(a)*step))
		
		for p in view:
			if (self.waypoint().position - self.position).angle(p.position - self.position) < math.pi/2:
				self.waypoint_clear()

class Stubborn(Unit):
	def __init__(self, position, goal):
		Unit.__init__(self, position, (goal-position).angle())
		self.last_view = ()
		self.goal = goal
		self.waypoint_push(goal)
	
	def think(self, dt, view):
		self.last_view = view

	def render(self, screen):
		Unit.render(self, screen)
		
def path_angle(start_angle, path):
	"""how much is the robot turning to reach the goal using this path"""
	a = abs(physics.angle_diff(start_angle, (Vec2d(*path[1])-Vec2d(*path[0])).angle()))
	for i in xrange(len(path)-2):
		a += abs((Vec2d(*path[i+1])-Vec2d(*path[i])).angle(Vec2d(*path[i+2])-Vec2d(*path[i+1])))
	return a
	
				
class AStarer(Stubborn):
	view_range = 75
	def __init__(self, position, goal):
		Stubborn.__init__(self, position, goal)
		self.goal = goal
		self.last_view = ()
		self.cdist = 10000000
		self.color = (255, 0,0)
		
	def think(self, dt, view):
		self.last_view = view
		ccourse = False
		last = self.position
		for i in xrange(self.waypoint_len()):
			for o in view:
				if graphs.linesegdist2(last, self.waypoint(i).position,	o.position) <= (self.radius + o.radius)**2:
					ccourse = True
					break
			last = self.waypoint(i).position
			if ccourse: break

		#result = graphs.random_roadmap(self, self.goal, view, graphs.SimpleGraphBuilder())
		result = graphs.random_roadmap(self, self.goal, view, graphs.GraphBuilder(self.speed, self.turningspeed))
	
		if ccourse is True:
			self.waypoint_clear()
			
		if result.success is True and (self.waypoint_len() == 0 or result.total_cost < self.cdist):
			self.waypoint_clear()
			for p in result.path:
				self.waypoint_push(Vec2d(*p))
			self.cdist = result.total_cost
	def render(self, screen):
		pygame.draw.line(screen, (255, 0, 0),
				self.goal + Vec2d(-10,-10), self.goal + Vec2d(10,10), 1)
		pygame.draw.line(screen, (255, 0, 0),
				self.goal + Vec2d(10,-10), self.goal + Vec2d(-10,10), 1)
		Stubborn.render(self, screen)
		pygame.draw.circle(screen, (255, 150, 150), 
			self.position, self.view_range, 1)
		for p in self.last_view:
			pygame.draw.circle(screen, (150, 255, 150),
				p.position, p.radius, 0)
		

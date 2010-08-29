from fast.physics import Vec2d
import obstacle
import pygame
import random
from pedestrians.randomwalker import RandomWalker, RandomWalkingAvoider #TODO: prettier imports
from pedestrians.stubborn import Stubborn
from unit import Unit
import math

class ScenarioRegistrar (type):
	"""Registers all scenarios that are declared, to let the user choose"""
	register = {}
	def __new__(cls, name, bases, dct):
		ret = ScenarioRegistrar.register[name] = type.__new__(cls, name, bases, dct)
		return ret

class Scenario(object): #abstract
	__metaclass__ = ScenarioRegistrar
	
	def __init__(self, world, agent, parameter):
		self.world = world
		self.agent = agent
		self.parameter = parameter
		self.world.add_unit(agent)
		self.world.add_obstacle(obstacle.Line(Vec2d(0,0), Vec2d(0, world.size[1])))
		self.world.add_obstacle(obstacle.Line(Vec2d(0, world.size[1]), Vec2d(world.size[0], world.size[1])))
		self.world.add_obstacle(obstacle.Line(Vec2d(world.size[0], world.size[1]), Vec2d(world.size[0], 0)))
		self.world.add_obstacle(obstacle.Line(Vec2d(world.size[0], 0), Vec2d(0,0)))
		
	def update(self, dt):
		pass
		
	def run(self):
		while 1:
			if self.agent.position == self.agent.goal:
				return True
				
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return False
			
			dt = self.world.advance()
			self.update(dt)

class RandomWalkers(Scenario):
	def __init__(self, world, agent, parameter):
		if parameter is None:
			parameter = 50
		super(RandomWalkers, self).__init__(world, agent, parameter)

		self.agent.position = Vec2d(10,10)
		self.agent.goal = Vec2d(*world.size)-self.agent.position
		self.agent.angle = (self.agent.goal-self.agent.position).angle()
		
		for i in xrange(self.parameter):
			init_position = self.agent.position
			while init_position.distance_to(self.agent.position) < 20:
				init_position = Vec2d(random.randrange(self.world.size[0]), random.randrange(self.world.size[1]))
			u = RandomWalkingAvoider()
			u.position = init_position
			self.world.add_unit(u)


class MarketSquare(Scenario):
	def __init__(self, world, agent, parameter):
		if parameter is None:
			parameter = 0 #dummy
			
		super(MarketSquare, self).__init__(world, agent, parameter)
		self.agent.position = Vec2d(10, 10)
		self.agent.goal = Vec2d(*world.size)-self.agent.position
		self.agent.angle = (self.agent.goal-self.agent.position).angle()
		
		for j in xrange(2):
			for i in xrange(4):
				self.world.add_obstacle(obstacle.Rectangle((i+1)*50 + 100*i, (j+1)*100 + 120*j - 50, 100, 120))

class CrowdedMarketSquare(Scenario):
	def __init__(self, world, agent, parameter):
		if parameter is None:
			parameter = 0
		super(self.__class__, self).__init__(world, agent, parameter)

		self.agent.position = Vec2d(10, 10)
		self.agent.goal = Vec2d(*world.size)-self.agent.position
		self.agent.angle = (self.agent.goal-self.agent.position).angle()

		rects = []
		for j in xrange(2):
			for i in xrange(4):
				r = obstacle.Rectangle((i+1)*50 + 100*i, (j+1)*100 + 120*j - 50, 100, 120)
				rects.append(r)
				self.world.add_obstacle(r)
				
		for i in xrange(parameter):
			good = False
			u = RandomWalkingAvoider()
			
			while not good: #generate random positions for pedestrians that are not inside obstacles...
				init_position = Vec2d(random.randrange(u.radius+1, self.world.size[0]-u.radius-1), 
									random.randrange(u.radius + 1, self.world.size[1] - u.radius - 1))
				good = init_position.distance_to(self.agent.position) > 20
				
				for r in rects:
					if not good:
						break
					good = good and not r._rect.inflate(u.radius*3, u.radius*3).collidepoint(init_position)

			u.position = init_position
			self.world.add_unit(u)
		
class Spawner(Scenario): #abstract
	def __init__(self, world, agent, parameter):
		super(Spawner, self).__init__(world, agent, parameter)
		self.crowd_rate = parameter

	def update(self, dt):
		super(Spawner, self).update(dt)
		exact = dt*self.crowd_rate
		numtospawn = int(exact)
		exact-=numtospawn
		if random.random() <= exact:
			numtospawn += 1
		self.spawn(numtospawn)
		
	def spawn(self, num_units):
		pass
	
class TheFlood(Spawner):
	def __init__(self, world, agent, parameter):
		if parameter is None:
			parameter = 3
		super(TheFlood, self).__init__(world, agent, parameter)
		
		agent.position = Vec2d(agent.radius*2, world.size[1]/2)
		agent.goal = Vec2d(world.size[0]-agent.radius*2, world.size[1]/2)
		agent.angle = (agent.goal-agent.position).angle()
		
		self.agent = agent
		
	def spawn(self, num_units):
		for u in self.world.units:
			if u is not self.agent and u.position.distance_to(u.goal) < 1:
				self.world.remove_unit(u)
			
		for i in xrange(num_units):	
			u = Stubborn()	
			
			u.position = Vec2d(self.world.size[0]-u.radius-1, random.randrange(u.radius, self.world.size[1]-u.radius))
			while u.position.distance_to(self.agent.goal) < 5*self.agent.radius:
				u.position = Vec2d(self.world.size[0]-u.radius-1, random.randrange(u.radius, self.world.size[1]-u.radius))
				
			u.goal = Vec2d(u.radius+1,random.randrange(u.radius, self.world.size[1]-u.radius))
			u.angle = (u.goal - u.position).angle()
			
			self.world.add_unit(u)

class Crossing(Spawner):
	def __init__(self, world, agent, parameter):
		if parameter is None:
			parameter = 3
		super(Crossing, self).__init__(world, agent, parameter)
		
		self.agent.position = Vec2d(10, world.size[1]/2)
		self.agent.goal = Vec2d(world.size[0]-10, world.size[1]/2)
		self.agent.angle = (self.agent.goal-self.agent.position).angle()
		
	def random_xpos(self, unit):
		return random.randrange(unit.radius+1, self.world.size[0]-unit.radius-1)

	def random_ypos(self, unit):
		return random.randrange(unit.radius+1, self.world.size[1]-unit.radius-1)
		
	def spawn(self, num_units):
		for u in self.world.units:
			if u is not self.agent and u.position.distance_to(u.goal) < 1:
				self.world.remove_unit(u)
			
		for i in xrange(num_units):
			u = Stubborn()
			
			if random.random() < 0.5: # coin toss
				# "horizontal" movement
				p1 = Vec2d( u.radius+1, self.random_ypos(u) )
				p2 = Vec2d( self.world.size[0]-u.radius-1, self.random_ypos(u) )
			else:
				# "vertical" movement
				p1 = Vec2d(self.random_xpos(u), u.radius+1)
				p2 = Vec2d(self.random_xpos(u), self.world.size[1]-u.radius-1)
				
			if random.random() < 0.5: # coin toss
				u.position = p1
				u.goal = p2
				u.angle = (p2-p1).angle()
			else:
				u.position = p2
				u.goal = p1
				u.angle = (p1-p2).angle()
				
			self.world.add_unit(u)

class Test(Scenario):
	def __init__(self, world, agent, parameter):
		if parameter is None:
			parameter = 50
		super(Test, self).__init__(world, agent, parameter)

		self.agent.position = Vec2d(200,200)
		self.agent.goal = Vec2d(400,200)
		self.agent.angle = 0

		u = Stubborn()
		u.position = Vec2d(300, 100)
		u.goal = Vec2d(300, 300)
		u.angle = math.pi/2
		
		self.world.add_unit(u)

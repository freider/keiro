from units import *
from fast.physics import Vec2d

class ScenarioRegistrar (type):
	"""Registers all scenarios that are declared, to let the user choose"""
	register = {}
	def __new__(cls, name, bases, dct):
		if name != "Scenario":
			print "Defining scenario %s"%(name,)
		ret = ScenarioRegistrar.register[name] = type.__new__(cls, name, bases, dct)
		return ret

class Scenario(object):
	__metaclass__ = ScenarioRegistrar
	
	def __init__(self, world, agent):
		self.world = world
		self.agent = agent
		self.world.addunit(agent)
		self.world.addcallback(self)
		
	def update(self, dt):
		pass
		
	def request_stop(self):
		return self.agent.position == self.agent.goal
		
	def run(self):
		self.world.run()

class RandomWalkers(Scenario):
	def __init__(self, world, agent, crowd_size):
		Scenario.__init__(self, world, agent)
		self.agent.position = Vec2d(10,10)
		self.agent.goal = Vec2d(*world.size)-self.agent.position
		self.agent.angle = (self.agent.goal-self.agent.position).angle()
		
		for i in xrange(crowd_size):
			init_position = self.agent.position
			while init_position.distance_to(self.agent.position) < 20:
				init_position = Vec2d(random.randrange(self.world.size[0]), random.randrange(self.world.size[1]))
			u = RandomWalker()
			u.position = init_position
			self.world.addunit(u)

class Spawner(Scenario): #abstract
	def __init__(self, world, agent, crowd_rate):
		Scenario.__init__(self, world, agent)
		self.crowd_rate = crowd_rate

	def update(self, dt):
		Scenario.update(dt)
		exact = dt*self.crowd_rate
		numtospawn = int(exact)
		exact-=numtospawn
		if random.random() <= exact:
			numtospawn += 1
		self.spawn(numtospawn)
		
	def spawn(self, num_units):
		pass
	
class TheFlood(Spawner):
	def __init__(self, world, agent, crowd_rate):
		Spawner.__init__(self, world, agent, crowd_rate)
		self.agent.position = Vec2d(10, world.size[1]/2)
		self.agent.goal = Vec2d(world.size[0]-10, world.size[1]/2)
		self.agent.angle = (self.agent.goal-self.agent.position).angle()
		
	def spawn(self, num_units):
		for u in self.world.units:
			if u.position.x<=0:
				self.world.removeunit(u)
			
		for i in xrange(num_units):		
			spawn_pos = Vec2d(self.world.size[0],random.randrange(self.world.size[1]))
			goal = Vec2d(-10,random.randrange(self.world.size[1]))
			self.world.addunit(Stubborn(spawn_pos, goal))

class Crossing(Spawner):
	def __init__(self, world, agent, crowd_rate):
		Spawner.__init__(self, world, agent, crowd_rate)
		self.agent.position = Vec2d(10, world.size[1]/2)
		self.agent.goal = Vec2d(world.size[0]-10, world.size[1]/2)
		self.agent.angle = (self.agent.goal-self.agent.position).angle()
		
	def spawn(self, num_units):
		for u in self.world.units:
			if u is not self.agent and u.position == u.goal:
				self.world.removeunit(u)
			
		for i in xrange(num_units):
			if random.random() < 0.5:
				spawn_pos = Vec2d(self.world.size[0]+10, random.randrange(self.world.size[1]))
				goal = Vec2d(-10,random.randrange(self.world.size[1]))
			else:
				spawn_pos = Vec2d(random.randrange(self.world.size[0]), self.world.size[1]+10)
				goal = Vec2d(random.randrange(self.world.size[0]), -10)
			if random.random() < 0.5:
				tmp = spawn_pos
				spawn_pos = goal
				goal = tmp
					
			self.world.addunit(Stubborn(spawn_pos, goal))

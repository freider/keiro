import time
import math
import random
import pygame
import sys

class Position(object):
	@property
	def x(self): return self.__pos[0]
	@property
	def y(self): return self.__pos[1]
	
	def __init__(self, *args):
		if len(args) == 1:
			args = args[0]
			if isinstance(args, Position):
				self.__pos = args.__pos
			elif isinstance(args, tuple):
				self.__pos = args
			else:
				raise TypeError
		elif len(args) == 2:
			self.__pos=(args[0],args[1])
		else: 
			raise TypeError(args)
	def __str__(self):
		return str(self.__pos);
	def __mul__(self, v):
		return Position(self.x*v, self.y*v)
	def __sub__(self, p):
		return Position(self.x-p.x, self.y-p.y)
	def __add__(self, p):
		return Position(self.x+p.x, self.y+p.y)
	def length(self):
		return math.sqrt(self.x*self.x + self.y*self.y)
	def norm(self):
		l = self.length()
		return Position(self.x/l, self.y/l)
	

class World(object):
	def __init__(self, size):
		self.units = [];
		self.size = size
	
	def addUnit(self, u):
		u.setWorld(self)
		self.units.append(u)
	
	def run(self):
		pygame.init()
		self.screen = pygame.display.set_mode(self.size)
		lasttime = time.clock()
		frames = 0
		while 1:
			newtime = time.clock()
			dt = newtime-lasttime
			if dt > 0 and frames > 0:
				fps = frames/dt if dt!=0 else -1
				#sys.stdout.write("%f FPS\r"%fps);
				#sys.stdout.flush()
				lasttime = newtime
				frames = 0
				
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					print "Bye bye"
					return
			#let everyone set targets
			for u in self.units:
				u.think();
			#move everyone and hope no one collides...				
			for u in self.units:
				diff = u.target - u.pos
				length = diff.length()
				maxlength = u.MAXSPEED*dt
				if length <= maxlength:
					u.pos = u.target
				#else:
				#	u.pos = u.pos + diff.norm()*maxlength
				
				
			self.render(self.screen)
			frames+=1
			
	def render(self, screen):
		screen.fill((0,0,0))
		for u in self.units:
			u.render(screen)
		pygame.display.flip()

class InteractionLayer(object):
	def __init__(self, viewpoint, targetworld):
		self.viewpoint = viewpoint
		self.targetworld = targetworld
			
class Unit(object):
	MAXSPEED = 10
	
	def __init__(self):
		self.place(Position(0,0))
		
	def place(self, pos):
		if isinstance(pos, Position):
			self.pos = self.target = Position(pos)
		else:
			raise TypeError
	
	def setTarget(self, target):
		self.target = target
		
	def think(self):
		raise NotImplementedError
		
	def render(self, screen):
		pygame.draw.circle(screen, (255, 255, 0), (int(self.pos.x), int(self.pos.y)), 10)

	def setWorld(self, homeworld):
		self.homeworld = homeworld

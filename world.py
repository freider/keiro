import time
import math
import random
import pygame
import sys

class World(object):
	def __init__(self):
		self.units = [];
		self.size = (320, 240)
	
	class Pos:
		def __init__(self, *pos):
			if len(pos) == 1:
				pos = pos[0]
				if isinstance(pos, World.Pos):
					self.x, self.y = pos.x, pos.y
				elif isinstance(pos, tuple):
					self.x, self.y = pos
				else:
					raise TypeError
			elif len(pos) == 2 and isinstance(pos[0], (float,int)) and isinstance(pos[1], (float,int)):
				self.x,self.y=pos[0],pos[1]
			else: 
				raise TypeError(pos)
			
		def __str__(self):
			return str((self.x, self.y));
		def scale(self, f):
			return World.Pos(self.x*f, self.y*f)
	
	def addUnit(self, u):
		self.units.append(u)
	
	def run(self):
		pygame.init()
		self.screen = pygame.display.set_mode(self.size)
		lasttime = time.clock()
		frames = 0
		while 1:
			newtime = time.clock()
			diff = newtime-lasttime
			if diff > 0 and frames > 0:
				fps = frames/diff if diff!=0 else -1
				#sys.stdout.write("%f FPS\r"%fps);
				#sys.stdout.flush()
				lasttime = newtime
				frames = 0
				
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					print "Bye bye"
					return
			for u in self.units:
				u.think();
			self.render(self.screen)
			frames+=1
			
	def render(self, screen):
		screen.fill((0,0,0))
		for u in self.units:
			u.render(screen)
		pygame.display.flip()
			
class Unit(object):
	MAX_STEP_LENGTH = 10
	def __init__(self, homeworld):
		self.homeworld = homeworld
		self.pos = World.Pos(homeworld.size).scale(0.5)
		homeworld.addUnit(self)
		
	def place(self, pos):
		self.pos = World.Pos(pos)
			
	def think(self):
		raise NotImplementedError
		
	def render(self, screen):
		pygame.draw.circle(screen, (255, 255, 0), (int(self.pos.x), int(self.pos.y)), 10)


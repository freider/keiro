import time
import random
import pygame
import sys
from position import Position	

class World(object):
	MAXFPS = 100 #max 100 on some systems
	MINDT = 1.0/MAXFPS
	def __init__(self, size):
		self.units = [];
		self.size = size
	
	def addUnit(self, u):
		u.setWorld(self)
		self.units.append(u)
	def removeUnit(self, u):
		self.units.remove(u)
	
	def run(self):
		pygame.init()
		self.screen = pygame.display.set_mode(self.size)
		lasttime = time.clock()
		frames = 0
		while 1:
			newtime = time.clock()
			dt = newtime-lasttime
			
			#if timestep is to small, wait for a bit
			if(dt < World.MINDT):
				continue
			
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
				#print "dt %f, dist %f:"%(dt, maxlength)
				if length <= maxlength:
					u.pos = u.target
				else:
					u.pos = u.pos + diff.norm()*maxlength
				
				
			self.render(self.screen)
			frames+=1
			
	def render(self, screen):
		screen.fill((0,0,0))
		for u in self.units:
			u.render(screen)
		pygame.display.flip()

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
		pygame.draw.circle(screen, (255, 255, 0), self.pos.toIntTuple(), 5)
		pygame.draw.line(screen, (140, 140, 255), self.pos.toIntTuple(), self.target.toIntTuple()) 

	def setWorld(self, homeworld):
		self.homeworld = homeworld
		

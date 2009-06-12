import time
import random
import pygame
import sys
from position import Position	

class World(object):
	MAX_FPS = 1000 #max 100 on some systems
	PRINT_FPS = True
	def __init__(self, size):
		self.units = [];
		self.size = size
		self.clock = pygame.time.Clock()
	
	def addUnit(self, u):
		u.setWorld(self)
		self.units.append(u)
	def removeUnit(self, u):
		self.units.remove(u)
	
	def run(self):
		pygame.init()
		self.screen = pygame.display.set_mode(self.size)
		while 1:
			dt = self.clock.tick(self.MAX_FPS)/1000.0

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
				else:
					u.pos = u.pos + diff.norm()*maxlength
			
			if self.PRINT_FPS:
				sys.stdout.write("%f fps           \r"%self.clock.get_fps())
			self.render(self.screen)
			
	def render(self, screen):
		screen.fill((0,0,0))
		for u in self.units:
			u.render(screen)
		pygame.display.flip()
		
	@staticmethod
	def checkCollision( p1_now, p2_now, 
						p1_later, p2_later, 
						p1_speed, p2_speed):
		return True
		

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
		pygame.draw.circle(screen, (255, 255, 0), self.pos.toIntTuple(), 5, 1)
		pygame.draw.line(screen, (140, 140, 255), self.pos.toIntTuple(), self.target.toIntTuple()) 

	def setWorld(self, homeworld):
		self.homeworld = homeworld
		

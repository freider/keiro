import time
import random
import pygame
import sys
from vector import vec2d

class World(object):
	#MAX_FPS = 1000 #max 100 on some systems
	PRINT_FPS = False
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
			dt = self.clock.tick()/1000.0

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					print "Bye bye"
					return
					
			moveplan = dict()
			#let everyone set targets
			for u in self.units:
				u.think();
				diff = u.target - u.pos
				length = diff.length
				maxlength = u.maxspeed*dt
				if length <= maxlength:
					newpos = vec2d(u.target)
				else:
					newpos = u.pos + diff.normalized()*maxlength
				moveplan[u] = newpos
				
			for u1,u1pos in moveplan.iteritems():
				collision = False
				for u2,u2pos in moveplan.iteritems():
					if u1 != u2 and u1pos.get_dist_sqrd(u2pos) < (u1.radius + u2.radius)**2:
						collision = True
						break
				if collision:
					u1.colliding = True
				else:
					u1.colliding = False
					u1.pos = u1pos
					
			
			if self.PRINT_FPS:
				sys.stdout.write("%f fps           \r"%self.clock.get_fps())
			self.render(self.screen)
			
	def render(self, screen):
		screen.fill((0,0,0))
		for u in self.units:
			u.render(screen)
		pygame.display.flip()
		
	@staticmethod
	def willCollide( p1_now, p1_later, p1_speed,
					p2_now,	 p2_later, p2_speed):
		r1 = pygame.Rect(p1_now, p1_later-p1_now)
		r2 = pygame.Rect(p2_now, p2_later-p2_now)
		if r1.colliderect(r2):
			#print r1, r2
			return True
		else:
			#print "hej"
			return False
		
class Unit(object):
	maxspeed = 10
	radius = 5
	def __init__(self):
		self.place(vec2d(0,0))
		self.colliding = False
		
	def place(self, pos):
		if isinstance(pos, vec2d):
			self.pos = self.target = vec2d(pos)
		else:
			raise TypeError
	
	def setTarget(self, target):
		self.target = target
		
	def think(self):
		raise NotImplementedError
		
	def render(self, screen):
		if self.colliding:
			color = (255,0,0)
		else:
			color = (255, 255, 0)
			
		pygame.draw.circle(screen, color, (int(self.pos.x), int(self.pos.y)), self.radius, 1)
		pygame.draw.line(screen, (140, 140, 255), self.pos, self.target) 

	def setWorld(self, homeworld):
		self.homeworld = homeworld
		

from fast.physics import Vec2d, Obstacle as ObstacleBase
import pygame

class Obstacle(object):
	def __init__(self):
		self.bounds = []

	def render(self, screen):
		color = pygame.Color("pink")
		for line in self.bounds:
			pygame.draw.line(screen, color, line.p1, line.p2)

class Line(Obstacle):
	def __init__(self, p1, p2):
		super(Line, self).__init__()
		self.bounds = (ObstacleBase(p1, p2),)
		
class Rectangle(Obstacle):
	def __init__(self, top, left, bottom, right):
		super(Rectangle, self).__init__()
		self._rect = pygame.Rect(left, top, right-left, bottom-top)#for pygame drawing
		
		self.bounds = ( ObstacleBase(Vec2d(top, left), Vec2d(top, right)), 
						ObstacleBase(Vec2d(top, right), Vec2d(bottom, right)),
						ObstacleBase(Vec2d(bottom, right), Vec2d(bottom, left)),
						ObstacleBase(Vec2d(bottom, left), Vec2d(top, left)) )		
	
	def render(self, screen):
		color = pygame.Color("blue")
		pygame.draw.rect(screen, color, self._rect, 1)
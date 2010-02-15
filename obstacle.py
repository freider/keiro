from fast.physics import LineSegment
import pygame

class Obstacle(LineSegment):
	def __init__(self, p1, p2):
		LineSegment.__init__(self, p1, p2)
		
	def render(self, screen):
		pygame.draw.line(screen, pygame.Color("pink"), self.p1, self.p2)
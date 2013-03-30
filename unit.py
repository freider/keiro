import pygame
import math
from fast.vector2d import Vec2d
from fast.particle import LinearParticle


class Unit(LinearParticle):
    color = (255, 255, 255)
    view_range = 0

    def __init__(self):
        super(Unit, self).__init__()
        self.radius = 8
        self.speed = 20
        self.turningspeed = 2 * math.pi / 3
        self.iteration_listeners = []

    def add_iteration_listener(self, listener):
        self.iteration_listeners.append(listener)

    def think(self, dt, view, debugsurface):
        pass

    def _think(self, *args, **kwargs):
        self.think(*args, **kwargs)

    def render(self, screen):
        pygame.draw.circle(screen, self.color,
            map(int, self.position), int(self.radius), 0)  # width=0 means filled circle
        pygame.draw.circle(screen, (0, 0, 0),
            map(int, self.position), int(self.radius), 2)

        #this draws a direction vector for a unit
        dirvector = map(int, (self.position.x + math.cos(self.angle) * self.radius, self.position.y + math.sin(self.angle) * self.radius))

        pygame.draw.line(screen, (0, 0, 0),
            map(int, self.position),
            dirvector, 2)

    def render_ID(self, screen, ID):
        myFont = pygame.font.SysFont("Arial", 8)
        idsurface = myFont.render(str(ID), 8, pygame.Color("black"))
        screen.blit(idsurface, map(int, self.position + Vec2d(-2, 4)))

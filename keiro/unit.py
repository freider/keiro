import pygame
import math
from vector2d import Vec2d
from particle import LinearParticle


class Unit(LinearParticle):
    color = (255, 255, 255)
    view_range = 0

    def __init__(self):
        super(Unit, self).__init__()
        self.radius = 8
        self.speed = 20
        self.turningspeed = 2 * math.pi / 3

    def think(self, dt, view, debugsurface):
        pass

    def _think(self, *args, **kwargs):
        self.think(*args, **kwargs)

    def render(self, screen):
        screen.circle(
            self.position,
            self.radius,
            self.color,
            0  # width=0 means filled circle
        )
        screen.circle(
            self.position,
            self.radius,
            (150, 150, 150),
            2
        )

        #this draws a direction vector for a unit
        dirvector = (
            self.position.x + math.cos(self.angle) * self.radius,
            self.position.y + math.sin(self.angle) * self.radius
        )

        screen.line(
            self.position,
            dirvector,
            (150, 150, 150),
            1
        )

    def render_ID(self, screen, ID):
        myFont = pygame.font.SysFont("Arial", 8)
        idsurface = myFont.render(str(ID), 8, pygame.Color("black"))
        screen.blit(idsurface, map(int, self.position + Vec2d(-2, 4)))

import pygame
import sys
import Image

from fast.particle import World as PhysicsWorld


class View(object):
    def __init__(self, obstacles, pedestrians):
        self.obstacles = obstacles
        self.pedestrians = pedestrians
        self.convex_hull = []

    def add_ch(self, ch):
        self.convex_hull = ch


class World(PhysicsWorld):
    def __init__(self, size, opts):
        PhysicsWorld.__init__(self)
        self.size = size
        self.units = []
        self.obstacles = []

        self.clock = pygame.time.Clock()
        self.timestep = opts.timestep
        self.fps = opts.fps
        self.encoders = []

        self.collision_list = []
        self.avg_groundspeed_list = []

    def add_unit(self, unit):
        self.units.append(unit)
        self.bind(unit)

    def remove_unit(self, unit):
        self.units.remove(unit)
        self.unbind(unit)

    def add_obstacle(self, obstacle):
        self.obstacles.append(obstacle)
        for line in obstacle.bounds:
            self.bind(line)

    def remove_obstacle(self, obstacle):
        for line in obstacle.bounds:
            self.unbind(line)
        self.obstacles.remove(obstacle)

    def add_encoder(self, encoder):
        self.encoders.append(encoder)

    def init(self):
        pygame.init()
        pygame.display.set_caption("Crowd Navigation")
        self._screen = pygame.display.set_mode(self.size)
        self._time = 0
        self._iterations = 0
        self.update(0)  # so we have no initial collisions
        self.debugsurface = pygame.Surface(self.size, masks=pygame.SRCALPHA).convert_alpha()

    def get_time(self):
        return self._time

    def advance(self):
        if self.timestep == 0:
            dt = self.clock.tick() / 1000.0  # use real time
        else:
            self.clock.tick()
            dt = self.timestep

        self._time += dt
        self._iterations += 1

        self.update(dt)

        self.debugsurface.fill((0, 255, 0, 0))

        for u in self.units:
            if u.view_range != 0:
                #view = View(self.get_obstacles(), self.particles_in_range(u, u.view_range))
                # Marc's occlusion code
                view = View(self.get_obstacles(), self.particles_in_view_range(u, u.view_range))  # (with occlusion)
            else:
                view = View(self.get_obstacles(), [])

            u.think(dt, view, self.debugsurface)

        if self.fps:
            sys.stdout.write("%f fps           \r" % self.clock.get_fps())
            sys.stdout.flush()

        self.render(self._screen)
        return dt

    def render(self, screen):
        screen.fill((255, 255, 255))

        for o in self.obstacles:
            o.render(screen)
        ID = 0
        for u in self.units:
            #u.render_ID(screen, ID)
            u.render(screen)
            ID = ID + 1

        screen.blit(self.debugsurface, (0, 0))

        pygame.display.flip()

        if len(self.encoders) > 0:
            mode = "RGB"
            imagestring = pygame.image.tostring(screen, mode)
            image = Image.fromstring(mode, self.size, imagestring)

            for enc in self.encoders:
                enc.add_frame(image)

import pygame
import sys

from particle import World as PhysicsWorld


class View(object):
    def __init__(self, obstacles, pedestrians):
        self.obstacles = obstacles
        self.pedestrians = pedestrians


class World(PhysicsWorld):
    def __init__(self, size):
        super(World, self).__init__()
        self.size = size
        self.units = []
        self.obstacles = []

        self.clock = pygame.time.Clock()
        self.timestep = 0  # default: real time
        self.show_fps = False
        self.encoders = []

        self.collision_list = []
        self.avg_groundspeed_list = []

    def init(self):
        pygame.init()
        pygame.display.set_caption("Crowd Navigation")
        self._screen = pygame.display.set_mode(self.size)
        self._time = 0
        self._iterations = 0
        self.update(0)  # so we have no initial collisions
        self.debugsurface = pygame.Surface(self.size, masks=pygame.SRCALPHA).convert_alpha()

    def set_timestep(self, timestep):
        self.timestep = timestep

    def set_show_fps(self, show=True):
        self.show_fps = show

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

        self.debugsurface.fill((0, 0, 0, 0))  # transparent

        for u in self.units:
            if u.view_range != 0:
                #view = View(self.get_obstacles(), self.particles_in_range(u, u.view_range))
                # Marc's occlusion code
                view = View(self.get_obstacles(), self.particles_in_view_range(u, u.view_range))  # (with occlusion)
            else:
                view = View(self.get_obstacles(), [])

            u._think(dt, view, self.debugsurface)

        if self.show_fps:
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
            for enc in self.encoders:
                enc.add_frame(imagestring)

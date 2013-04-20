import unittest
import math
from keiro.particle import World, LinearParticle
from keiro.vector2d import Vec2d


class VectorTest(unittest.TestCase):
    def setUp(self):
        self.a = Vec2d(3, 15.5)
        self.b = Vec2d(7.3, 4)

    def test_str(self):
        assert str(self.a) == "Vec2d(3.000000,15.500000)"


class ParticleTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_create(self):
        p = LinearParticle(1, 5)
        self.assertEqual(p.angle, 1)
        self.assertEqual(p.position.x, 1)
        self.assertEqual(p.position.y, 5)

    def test_update(self):
        p = LinearParticle(1, 5, 0)
        p.speed = 1
        p.turningspeed = 3 * math.pi / 4
        goal = Vec2d(0, 4)
        p.waypoint_push(goal)
        p.update(1)
        self.assertAlmostEqual(p.position.x, 1)
        self.assertAlmostEqual(p.position.y, 5)
        self.assertAlmostEqual(p.angle, -3 * math.pi / 4)
        p.update(math.sqrt(2) * 0.99)
        self.assertAlmostEqual(p.position.x, 0.01, 6)
        self.assertAlmostEqual(p.position.y, 4.01, 6)
        p.update(10)
        self.assertEqual(p.position, goal)


class WorldTests(unittest.TestCase):
    def setUp(self):
        self.world = World()

    def test_particle_collision(self):
        p1 = LinearParticle(10, 10)
        p2 = LinearParticle(12, 10)
        p2.radius = p1.radius = 10

        self.world.bind(p1)
        self.world.bind(p2)
        self.world.update(0)

        self.assertEquals(p1.position.y, p2.position.y)
        self.assertEquals(p2.position.x - p1.position.x, 20)
        self.assertEquals(p1.collisions, 1)
        self.assertEquals(p2.collisions, 1)
        self.world.update(0)
        self.assertEquals(p1.collisions, 1)
        self.assertEquals(p2.collisions, 1)

if __name__ == "__main__":
    print unittest.main()

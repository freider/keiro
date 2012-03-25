import unittest
import math


class VectorTest(unittest.TestCase):
    def setUp(self):
        import vector2d
        self.a = vector2d.Vec2d(3, 15.5)
        self.b = vector2d.Vec2d(7.3, 4)

    def test_str(self):
        assert str(self.a) == "Vec2d(3.000000,15.500000)"


class ParticleTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_create(self):
        import particle
        p = particle.LinearParticle(1, 5)
        self.assertEqual(p.angle, 1)
        self.assertEqual(p.position.x, 1)
        self.assertEqual(p.position.y, 5)

    def test_update(self):
        import particle
        import vector2d
        p = particle.LinearParticle(1, 5, 0)
        p.speed = 1
        p.turningspeed = 3 * math.pi / 4
        goal = vector2d.Vec2d(0, 4)
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


if __name__ == "__main__":
    print unittest.main()

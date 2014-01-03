import random
import unittest
from vector2d import Vec2d
import numpy as np


class StateGenerator(object):
    """Generate random 2d points within supplied rectangle"""
    def __init__(self, minx, maxx, miny, maxy):
        self.minx = minx
        self.maxx = maxx
        self.miny = miny
        self.maxy = maxy

    def generate(self):
        posx = self.minx + random.random() * (self.maxx - self.minx)
        posy = self.miny + random.random() * (self.maxy - self.miny)
        return Vec2d(posx, posy)

    def generate_n(self, n):
        for i in xrange(n):
            yield self.generate()


class PrependedGenerator(StateGenerator):
    """Allows bias of the generator by prepending the random queue with non-random points"""
    def __init__(self, minx, maxx, miny, maxy):
        super(PrependedGenerator, self).__init__(minx, maxx, miny, maxy)
        self.biaspoints = []

    def prepend(self, point):
        self.biaspoints.append(point)

    def generate(self):
        if len(self.biaspoints) > 0:
            ret = self.biaspoints[0]
            del self.biaspoints[0]
            return ret
        else:
            return super(PrependedGenerator, self).generate()


class ExtendingGenerator(PrependedGenerator):
    """Extending the target area for each generated point"""
    def __init__(self, minarea, maxarea, steps):
        self.n = 0
        self.steps = steps
        endarray = np.array(maxarea)
        startarray = np.array((
            max(endarray[0], minarea[0]),
            min(endarray[1], minarea[1]),
            max(endarray[2], minarea[2]),
            min(endarray[3], minarea[3])
        ))
        self.diff = (endarray - startarray) / float(steps)
        super(ExtendingGenerator, self).__init__(*startarray)

    def generate(self):
        ret = super(ExtendingGenerator, self).generate()
        #extend area
        if self.n < self.steps:
            self.minx += self.diff[0]
            self.maxx += self.diff[1]
            self.miny += self.diff[2]
            self.maxy += self.diff[3]
        self.n += 1
        return ret


class TestGenerators(unittest.TestCase):
    def setUp(self):
        self.minx = 100
        self.maxx = 200
        self.miny = -200
        self.maxy = -100
        self.sg = StateGenerator(100, 200, -200, -100)
        self.pg = PrependedGenerator(100, 200, -200, -100)

    def test_sg(self):
        for pos in self.sg.generate_n(100):
            self.assertTrue(pos.x >= self.minx and pos.x <= self.maxx)
            self.assertTrue(pos.y >= self.miny and pos.y <= self.maxy)

    def test_pg(self):
        bias = self.sg.generate()
        self.assertTrue(self.pg.generate() != bias)
        self.pg.prepend(bias)
        self.assertTrue(self.pg.generate() == bias)
        self.assertTrue(self.pg.generate() != bias)
        bias2 = self.sg.generate()
        self.pg.prepend(bias)
        self.pg.prepend(bias2)
        self.assertTrue(self.pg.generate() == bias and self.pg.generate() == bias2)


if __name__ == "__main__":
    unittest.main()

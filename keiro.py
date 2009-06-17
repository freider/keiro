from world import *
from variousunits import *
import math
import random

if __name__ == "__main__":
	w = World((640, 480))
	for i in xrange(50):
		intelligence = RandomWalker()
		init_position = vec2d(random.randrange(w.size[0]), random.randrange(w.size[1]))
		w.addUnit(init_position, intelligence)
	w.run()

from world import *
from variousunits import *
import math
import random
import cProfile

if __name__ == "__main__":
	w = World((640, 480))
	for i in xrange(300):
		init_position = Vec2d(random.randrange(w.size[0]), random.randrange(w.size[1]))
		w.addUnit(RandomWalker(init_position))
	w.addUnit(Stubborn((0,0), w.size))	
	#cProfile.run("w.run()")
	w.run()

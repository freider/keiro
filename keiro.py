from world import *
from variousunits import *
import math
import random
import time
import cProfile

if __name__ == "__main__":
	random.seed(2)
	w = World((640, 480))
	for i in xrange(300):
		init_position = Vec2d(random.randrange(w.size[0]), random.randrange(w.size[1]))
		w.addUnit(RandomWalker(init_position))
	vip = AStarer((0,0), w.size)
	w.addUnit(vip)
	w.trackUnit(vip)
	pretime = time.clock()	
#	w.RENDER = False
	#cProfile.run("w.run()")
	print w.run()
	print "Time:", time.clock() - pretime, "s"

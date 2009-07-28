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
	vip = AStarer(Vec2d(10,10), w.size)
	#stubborn = Stubborn(Vec2d(0,10), w.size)
	w.addUnit(vip)
	#w.addUnit(stubborn)
	w.trackUnit(vip)
	
	pretime = time.clock()	
#	w.RENDER = False
	#cProfile.run("w.run()")
	w.run()
	total_time = time.clock() - pretime
	print "Collision count:", w.tracked_unit.collisions
	#print "Travelled distance:", w.tracked_unit.total_distance, "units"
	print "World Time:", w.runtime, "s"
	print "Real Time:", total_time, "s"
	print "Average iteration time:", total_time/w.iterations, "s"

from world import *
from variousunits import *
import math
import random
import time
import cProfile
from getopt import getopt
import sys

if __name__ == "__main__":
	opts, argv = getopt(sys.argv[1:], "n:fp", ["num-people=", "fps", "profile", "norender", "realtime"])
	#Defaults
	random.seed(1)
	crowd_size = 300
	profiling = False
	render = True
	timestep = 0.1
	fps = False
	
	for opt,arg in opts:
		print (opt,arg)
		if opt in ("--norender",):
			render = False
		elif opt in ("--realtime",):
			timestep = 0
		elif opt in ("--num-people", "-n"):
			crowd_size = int(arg)
		elif opt in ("--fps", "-f"):
			fps = True
		elif opt in ("--profile", "-p"):
			profiling = True
	
	
	w = World((640, 480))
	w.RENDER = render
	w.timestep = timestep
	w.PRINT_FPS = fps
	vip = AStarer(Vec2d(10,10), w.size)
	w.addUnit(vip)

	for i in xrange(crowd_size):
		init_position = vip.position#dummy
		while init_position.distance_to(vip.position) < 20:
			init_position = Vec2d(random.randrange(w.size[0]), random.randrange(w.size[1]))
		w.addUnit(RandomWalker(init_position))
		
	w.trackUnit(vip)
	
	pretime = time.clock()	
	if profiling:
		cProfile.run("w.run()")
	else:
		w.run()
	total_time = time.clock() - pretime
	print "Collision count:", w.tracked_unit.collisions
	#print "Travelled distance:", w.tracked_unit.total_distance, "units"
	print "World Time:", w.runtime, "s"
	print "Real Time:", total_time, "s"
	print "Average iteration time:", total_time/w.iterations, "s"

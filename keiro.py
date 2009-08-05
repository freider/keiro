#!/usr/bin/env python
from world import *
from units import *
import math
import random
import time
import cProfile
from getopt import getopt
import sys
import scenarios

if __name__ == "__main__":
	opts, argv = getopt(sys.argv[1:], "n:fpt:s:", ["num-people=", "fps", "profile", "timestep=", "scenario=","norender"])
	#Defaults
	random.seed(2)
	crowd_size = 300
	profiling = False
	render = True
	timestep = 0.1
	fps = False
	scenario_class = scenarios.RandomWalkers
	
	for opt,arg in opts:
		if opt in ("--norender",):
			render = False
		elif opt in ("--num-people", "-n"):
			crowd_size = int(arg)
		elif opt in ("--fps", "-f"):
			fps = True
		elif opt in ("--profile", "-p"):
			profiling = True
		elif opt in ("--timestep", "-t"):
			timestep = float(arg)
		elif opt in ("--scenario", "-s"):
			print "==========="
			scenario_class = scenarios.ScenarioRegistrar.register[arg]

	
	world = World((640, 480))
	world.RENDER = render
	world.timestep = timestep
	world.PRINT_FPS = fps

	agent = AStarer(Vec2d(0,0), Vec2d(*world.size))
	scenario = scenario_class(world, agent, crowd_size)
	
	pretime = time.clock()	
	if profiling:
		cProfile.run("scenario.run()")
	else:
		scenario.run()
	
	total_time = time.clock() - pretime
	print "Collision count:", agent.collisions
	#print "Travelled distance:", w.tracked_unit.total_distance, "units"
	print "World Time:", world.runtime, "s"
	print "Real Time:", total_time, "s"
	print "Average iteration time:", total_time/world.iterations, "s"
	


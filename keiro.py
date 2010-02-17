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
import pickle
import os
from datetime import datetime

#import psyco
#psyco.full()
os.environ["DJANGO_SETTINGS_MODULE"] = "stats.settings"
from stats.statsapp import models

settings = dict(
	seed = 2,
	crowd_size = 10,
	timestep = 0.1,
	scenario_name = "RandomWalkers",
	ai_name = "Stubborn",
	draw_fps = False,
	profiling = False,
	render = True,
	verbose = False,
	world_size = (640,480),
	capture = False
	)

def print_options():
	print pickle.dump(scenarios.ScenarioRegistrar.register, sys.stdout)

if __name__ == "__main__":
	opts, argv = getopt(sys.argv[1:], "n:fpt:s:lc", ["num-people=", "fps", "profiling", "timestep=", "scenario=", "list-options", "norender", "capture"])
	
	for opt,arg in opts:
		if opt in ("--norender",):
			settings['render'] = False
		elif opt in ("--num-people", "-n"):
			settings['crowd_size'] = int(arg)
		elif opt in ("--fps", "-f"):
			settings['draw_fps'] = True
		elif opt in ("--profiling", "-p"):
			settings['profiling'] = True
		elif opt in ("--timestep", "-t"):
			settings['timestep'] = float(arg)
		elif opt in ("--scenario", "-s"):
			settings['scenario_name'] = arg
		elif opt in ("--verbose", "-v"):
			settings["verbose"] = True
		elif opt in ("--capture", "-c"):
			settings["capture"] = True
		else:
			print_options()
			quit()
	
	
	random.seed(settings['seed'])
	
	world = World(settings['world_size'], settings)
	agent_class = UnitRegistrar.register[settings['ai_name']]
	agent = agent_class()
	scenario_class = scenarios.ScenarioRegistrar.register[settings['scenario_name']]
	scenario = scenario_class(world, agent, settings['crowd_size'])
		
	pretime = time.clock()	
	if settings['profiling']:
		cProfile.run("scenario.run()")
	else:
		scenario.run()
	
	total_time = time.clock() - pretime
	
	record = models.Run()
	record.date = datetime.now()
	record.scenario_name = settings['scenario_name']
	record.seed = settings['seed']
	record.ai_name = settings['ai_name']
	record.timestep = settings['timestep']
	record.collisions = agent.collisions
	record.avg_iteration_time = total_time/world.iterations
	
	record.save()
	
	# print "Collision count:", 
	# #print "Travelled distance:", w.tracked_unit.total_distance, "units"
	# print "World Time:", world.runtime, "s"
	# print "Real Time:", total_time, "s"
	# print "Average iteration time:", total_time/world.iterations, "s"


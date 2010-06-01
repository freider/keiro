#!/usr/bin/env python
from world import World, View
import pedestrians
from agents import *
from scenarios import *
from scenario import ScenarioRegistrar
from agent import AgentRegistrar
from iterations import IterationRegister

import mencoder

import os
import random
import cProfile
from optparse import OptionParser
from datetime import datetime

os.environ["DJANGO_SETTINGS_MODULE"] = "stats.settings"
from stats.statsapp import models

if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option("-s", "--scenario", default="RandomWalkers50")
	parser.add_option("-a", "--agent", default="RoadMap")
	parser.add_option("-r", "--seed", type="int", default=1)
	parser.add_option("-t", "--timestep", type="float", default=0.1)
	
	parser.add_option("-f", "--fps", action="store_true", default=False)
	parser.add_option("-p", "--profile", action="store_true", default=False)
	parser.add_option("-c", "--capture", metavar="PATH")
	
	(opts, args) = parser.parse_args()

	random.seed(opts.seed)
	ScenarioClass = ScenarioRegistrar.register[opts.scenario]
	AgentClass = AgentRegistrar.register[opts.agent]
	
	agent = AgentClass()
	iterations = IterationRegister()
	agent.add_iteration_listener(iterations)
	
	world = World((640, 480), opts) #TODO: refactor world creation to each scenario (scenario should decide world size etc.)
	
	if opts.capture != None:
		encoder = mencoder.Encoder()
		world.add_encoder(encoder)
		
	scenario = ScenarioClass(world, agent)
	world.init()
	agent.init(View(world.get_obstacles(), []))
	
	if opts.profile:
		cProfile.run("scenario.run()")
	else:
		if scenario.run():
			record = models.Record()
			record.date = datetime.now()
			record.scenario = opts.scenario
			record.seed = opts.seed
			record.agent = opts.agent
			record.view_range = agent.view_range
			record.timestep = opts.timestep
			record.collisions = agent.collisions
			record.avg_iteration_time = iterations.get_avg_iterationtime()
			record.max_iteration_time = iterations.get_max_iterationtime()
			record.min_iteration_time = iterations.get_min_iterationtime()
			record.completion_time = world.get_time()
			record.save()
			print("Saved record to database")
		else:
			print("User triggered quit, no record saved to database")
			
	if opts.capture != None and opts.timestep != 0:
		encoder.encode(int(1/opts.timestep), opts.capture)
		encoder.cleanup()
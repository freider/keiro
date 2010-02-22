#!/usr/bin/env python
from world import *
from units import *
import math
import random
import time
import cProfile
from optparse import OptionParser
import sys
import scenarios
import pickle
import os
from datetime import datetime

os.environ["DJANGO_SETTINGS_MODULE"] = "stats.settings"
from stats.statsapp import models

if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option("-s", "--scenario", default="RandomWalkers")
	parser.add_option("-a", "--agent", default="Stubborn")
	parser.add_option("-r", "--seed", type="int", default=1)
	parser.add_option("-t", "--timestep", type="float", default=0.1)
	
	parser.add_option("-f", "--fps", action="store_true", default=False)
	parser.add_option("-p", "--profile", action="store_true", default=False)
	parser.add_option("--no-render", action="store_true", default=False)
	parser.add_option("-c", "--capture", metavar="PATH")
	
	(opts, args) = parser.parse_args()
	
	random.seed(opts["seed"])
	ScenarioClass = scenarios.ScenarioRegistrar.register[otps["scenario"]]
	AgentClass = UnitRegistrar.register[opts["agent"]]
	agent = AgentClass()
	world = World((640, 480), settings)
	scenario = ScenarioClass(world, agent)
	
	if opts["profile"]:
		cProfile.run("scenario.run()")
	else:
		scenario.run()
	
	record = models.Run()
	record.date = datetime.now()
	record.scenario_name = settings["scenario_name"]
	record.seed = opts["seed"]
	record.ai_name = opts["agent"]
	record.timestep = opts["timestep"]
	record.collisions = agent.collisions
	record.avg_iteration_time = total_time/world.iterations
	
	record.save()
#!/usr/bin/env python
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
from statsapp.models import Record
import Gnuplot, Gnuplot.funcutils
from numpy import *

def apara_vs_collisions(groups):
	plotdata = []
	
	for xval in sorted(groups.keys()):
		s = 0
		n = 0
		for r in groups[xval]:
			s += r.collisions
			n += 1
		yval = float(s)/n
		plotdata.append((xval, yval))
			
	return plotdata
	
def apara_vs_ttg(groups):
	plotdata = []
	
	for xval in sorted(groups.keys()):
		s = 0
		n = 0
		for r in groups[xval]:
			s += r.completion_time
			n += 1
		yval = float(s)/n
		plotdata.append((xval, yval))

	return plotdata

def apara_vs_itertime(groups):
	plotdata = []
	for xval in sorted(groups.keys()):
		s = array(4*[0.0])
		n = 0
		for r in groups[xval]:
			s += array([xval, r.avg_iteration_time, r.min_iteration_time, r.max_iteration_time])
			n += 1
		xyval = s/n
		plotdata.append(xyval)

	return plotdata



def tab_separated_string(plotdata):
	return '\n'.join(['\t'.join(map(str, r)) for r in plotdata])

def plot(plotdata, outfile = None):
	g = Gnuplot.Gnuplot()
	if len(plotdata[0]) == 2:
		g('set data style linespoints')
	elif len(plotdata[0]) == 4:
		g('set data style yerrorlines')
		
	g.plot(plotdata)
	if outfile:
		g.hardcopy(outfile, enhanced = 1, color = 0)
		
if __name__ == "__main__":
	from optparse import OptionParser
	parser = OptionParser()
	parser.add_option("-s", "--scenario", default="RandomWalkers")
	parser.add_option("-S", "--scenarioparameter", type="int", default = 50)
	parser.add_option("-a", "--agent", default="RoadMap")
	parser.add_option("-A", "--agentparameter", type="int")
	(opts, args) = parser.parse_args()
	
	agent = opts.agent
	scenario = opts.scenario
	scenario_parameter = opts.scenarioparameter

	qs = Record.objects.filter(agent = agent, scenario = scenario, scenario_parameter = scenario_parameter)
	groups = {}
	#grouping by key
	for r in qs:
		key = r.agent_parameter
		if key in groups:
			groups[key].append(r)			
		else:
			groups[key] = [r]

	
	if args:
		outfile = args[0]
	else:
		outfile = None

	data = apara_vs_itertime(groups)
	#print data
	#quit()
	if data:
		plot(data, outfile)
	else:
		print "No data available"
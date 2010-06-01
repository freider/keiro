import pygame
import math
import random
from agent import Agent, iteration
import graphs
from fast import graphutils, physics
from fast.physics import Vec2d, linesegdist2, line_distance2, angle_diff
from stategenerator import PrependedGenerator

class RoadMap(Agent):
	def __init__(self):
		super(RoadMap, self).__init__()
		self.cdist = 10000000
	
	@iteration	
	def think(self, dt, view, debugsurface):		
		if not self.goal: #have no goal?
			return
		#debugsurface.fill((255, 0, 0, 100))
		ccourse = False
		last = self.position
		for i in xrange(self.waypoint_len()):
			for o in view.pedestrians:
				if graphs.linesegdist2(last, self.waypoint(i).position,	o.position) <= (self.radius + o.radius)**2:
					ccourse = True
					break
			last = self.waypoint(i).position
			if ccourse: break

		graphbuilder = graphs.GraphBuilder(self.speed, self.turningspeed)
		
		safe_distance = self.radius+1 #some margin is nice
		start = graphbuilder.node(self.position, self.angle)
		end = graphbuilder.node(self.goal, None)

		if graphs.free_path(self.position, self.goal, view, safe_distance):
			graphbuilder.connect(self.position, self.goal)
		else:
			for i in xrange(10): #global planning
				newpos = Vec2d(640*random.random(), 480*random.random())
				for pos in graphbuilder.positions():
					if graphs.free_path(Vec2d(*pos), newpos, view, safe_distance):
						graphbuilder.connect(pos, newpos)
						pygame.draw.aaline(debugsurface, (0,255,0,255), pos, newpos)

			for i in xrange(10): #some extra local points to handle the crowd
				newpos = self.position + Vec2d((2*random.random()-1)*self.view_range, (2*random.random()-1)*self.view_range)
				for pos in graphbuilder.positions():
					if graphs.free_path(Vec2d(*pos), newpos, view, safe_distance):
						graphbuilder.connect(pos, newpos)
						pygame.draw.aaline(debugsurface, (0,255,0,255), pos, newpos)
						
			for p in graphbuilder.positions():
				pygame.draw.circle(debugsurface, (0,0,0), p, 2, 0)

		nodes = graphbuilder.all_nodes()
		result = graphutils.shortest_path(start, end, nodes)
		if result.success:
			result.path = [tuple(self.position)]
			for i in result.indices:
				if result.path[-1] != nodes[i].position:
					result.path.append(nodes[i].position)
		
	
		if ccourse is True:
			self.waypoint_clear()
			
		if result.success is True and (self.waypoint_len() == 0 or result.total_cost < self.cdist):
			self.waypoint_clear()
			for p in result.path:
				self.waypoint_push(Vec2d(*p))
			self.cdist = result.total_cost
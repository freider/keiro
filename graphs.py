from random import random
from fast.physics import Vec2d, linesegdist2, line_distance2, angle_diff
from fast.graphutils import *
import math
import pygame
				
def free_path(p1, p2, view, safe_distance = 0):
	for p in view.pedestrians:
		safedistsquare = (safe_distance + p.radius)**2
		if linesegdist2(p1, p2, p.position) <= safedistsquare:
			return False

	safedistsquare = safe_distance**2
	for o in view.obstacles:
		if line_distance2(p1, p2, o.p1, o.p2) <= safedistsquare:
			return False
			
	return True

class SimpleGraphBuilder(object):
	def __init__(self):
		self.graph = {} #position => node
				
	def connect(self, p1, p2):
		p1 = tuple(p1)
		p2 = tuple(p2)
		v1 = Vec2d(*p1)
		v2 = Vec2d(*p2)
		n1 = self.node(p1)
		n2 = self.node(p2)
		cost = v1.distance_to(v2)
		n1.connect(cost, n2)
		n2.connect(cost, n1)
	
	def node(self, position, angle = None):
		position = tuple(position)
		if position not in self.graph:
			tmp = self.graph[position] = Node()
			tmp.est_cost_there = 0 #TODO
			tmp.position = position
			return tmp
		else:
			return self.graph[position]
	
	def all_nodes(self):
		return self.graph.values()
	
	def positions(self):
		return self.graph.keys()
		
class GraphBuilder(object):
	"""Builds a graph for navigating R2 with penalties for distance and turning"""
	def __init__(self, speed, turning_speed):
		self.graph = {} # position => angle => nodes
		self.speed = speed
		self.turning_speed = turning_speed
		
	def connect(self, p1, p2):
		p1 = tuple(p1)
		p2 = tuple(p2)
		v1 = Vec2d(*p1)
		v2 = Vec2d(*p2)
		if p1 not in self.graph:
			self.graph[p1] = {}
		if p2 not in self.graph:
			self.graph[p2] = {}
		
		diff = v2-v1
		cost = diff.length()/self.speed
		angle = diff.angle()
		comp_angle = angle_diff(angle, math.pi)
		
		#print cost
		self.node(p1, angle).connect(cost, self.node(p2, angle))
		self.node(p2, comp_angle).connect(cost, self.node(p1, comp_angle))
						
	def node(self, position, angle):
		position = tuple(position)
		if position not in self.graph:
			edges = self.graph[position] = {}
		else:
			edges = self.graph[position]		
		
		if angle in edges:
			node = edges[angle]
		else:
			node = Node()
			node.position = position
			node.angle = angle
			node.est_cost_there = 0 #TODO
			for a,n in edges.items():
				if angle is None or a is None:
					cost = 0
				else:
					cost = abs(angle_diff(a,angle))/self.turning_speed
				n.connect(cost, node)
				node.connect(cost, n)
			edges[angle] = node
		return node
	
	def all_nodes(self):
		nodes = []
		for position,edges in self.graph.items():
			for angle,node in edges.items():
				nodes.append(node)
		return nodes
		
	def positions(self):
		return self.graph.keys()

if __name__ == "__main__":
	gb = GraphBuilder(1, math.pi/4)
	gb.connect((0,0), (1,0))
	gb.connect((1,0), (1,1))
		
	start = gb.node((0,0), 0)
	end = gb.node((1,1), None)
	nodes = gb.all_nodes()
	#print [(n.position, n.angle) for n in nodes]
	
	#print end.position
	result = shortest_path(start, end, nodes)
	if result.success:
		result.path = [(nodes[i].cost_here, nodes[i].angle, nodes[i].position) for i in result.indices]
		print result.total_cost, result.path
	else:
		print "fail!"

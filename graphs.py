from random import random
from physics import Vec2d, linesegdist2, angle_diff
from graphutils import *
import math

def free_path(p1, p2, obstacles, safe_distance = 0):
	for o in obstacles:
		if linesegdist2(p1, p2, o.position) <= (o.radius+safe_distance)**2:
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

def random_roadmap(me, target_position, obstacles, graphbuilder):
	safe_distance = me.radius+1
	start = graphbuilder.node(me.position, me.angle)
	end = graphbuilder.node(target_position, None)
	
	if free_path(me.position, target_position, obstacles, safe_distance):
		graphbuilder.connect(me.position, target_position)
	else:
		while len(graphbuilder.positions()) < 20:
			newpos = me.position + Vec2d((2*random()-1)*me.view_range, (2*random()-1)*me.view_range)
			for pos in graphbuilder.positions():
				if free_path(Vec2d(*pos), newpos, obstacles, safe_distance):
					graphbuilder.connect(pos, newpos)
					
	nodes = graphbuilder.all_nodes()
	result = shortest_path(start, end, nodes)
	if result.success:
		result.path = [tuple(me.position)]
		for i in result.indices:
			if result.path[-1] != nodes[i].position:
				result.path.append(nodes[i].position)
	return result
		
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

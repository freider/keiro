from random import random
from fast.physics import Vec2d, linesegdist2, angle_diff
from fast.graphutils import *
import math

def line_distance2(l11, l12, l21, l22):
	sign = lambda x:0 if x==0 else x/abs(x)
	if sign((l21 - l11).cross(l22 - l11)) != sign((l21 - l12).cross(l22 - l12)) and \
		sign((l11 - l21).cross(l12 - l21)) != sign((l11 - l22).cross(l12 - l22)):
		return 0
	return min(linesegdist2(l11, l12, l21), linesegdist2(l11, l12, l22),
				linesegdist2(l21, l22, l11), linesegdist2(l21, l22, l12))
				
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

def random_roadmap(me, target_position, view, graphbuilder):
	safe_distance = me.radius+1
	start = graphbuilder.node(me.position, me.angle)
	end = graphbuilder.node(target_position, None)
	
	if free_path(me.position, target_position, view, safe_distance):
		graphbuilder.connect(me.position, target_position)
	else:
		for i in xrange(30):
			newpos = me.position + Vec2d((2*random()-1)*me.view_range, (2*random()-1)*me.view_range)
			for pos in graphbuilder.positions():
				if free_path(Vec2d(*pos), newpos, view, safe_distance):
					graphbuilder.connect(pos, newpos)
					
	nodes = graphbuilder.all_nodes()
	result = shortest_path(start, end, nodes)
	if result.success:
		result.path = [tuple(me.position)]
		for i in result.indices:
			if result.path[-1] != nodes[i].position:
				result.path.append(nodes[i].position)
	return result

class ARTBuilder(object):
	class node:
		def __init__(self, position, angle, parent = None, time = 0, free_prob = 1):
			self.position = position
			self.angle = angle
			self.time = time
			self.parent = parent
			self.free_prob = free_prob
	
	def _free_prob(self, me, me_start, start_angle, me_end, start_time):
		diff = me_start - me_end
		end_time = start_time + angle_diff(start_angle, diff.angle())/me.turningspeed + diff.length()/me.speed
		for p in self.view.pedestrians:
			p_start = p.position + p.velocity*start_time
			p_end = p.position + p.velocity*end_time
			if line_distance2(me_start, me_end, p_start, p_end) <= (me.radius+p.radius)**2:
				return (0, end_time)
				
		#todo: add support for obstacles
		return (1, end_time)
		
	def build(self, me, target_position, view, max_size):
		self.view = view
		
		start = ARTBuilder.node(me.position, me.angle)
		if self._free_prob(me, me.position, me.angle, target_position, 0)[0] > 0.9:
			return [me.position, target_position] #direct path
		
		nodes = [ARTBuilder.node(me.position, me.angle, parent = None, time = 0, free_prob = 1)]
		#always use the nodes from the last solution in this iterations so they are kept if still good enough
		trypos = [me.waypoint(i).position for i in xrange(me.waypoint_len())]
		while len(trypos) < max_size:
			trypos.append(me.position + Vec2d((2*random()-1)*me.view_range, (2*random()-1)*me.view_range))
		for me_end in trypos:
			best = None
			for n in nodes:
				me_start = n.position
				free_prob, end_time = self._free_prob(me, me_start, n.angle, me_end, n.time)
				new_prob = free_prob * n.free_prob
				if new_prob > 0.9:
					if best is None or best[1] > end_time:
						best = (new_prob, end_time, n)
						
			if best is not None:
				new_prob, new_time, parent = best[0], best[1], best[2]
				newnode = ARTBuilder.node(me_end, (me_end - n.position).angle(), parent = parent, time = new_time, free_prob = new_prob)
				nodes.append(newnode)
				#check if the new node has a good enough path to the goal
				free_prob, end_time = self._free_prob(me, newnode.position, newnode.angle, target_position, new_time)
				target_prob = free_prob*new_prob
				if target_prob > 0.9:
					path = [target_position]
					n = newnode
					while n != None:
						path.append(n.position)
						n = n.parent
					path.reverse()
					return path
			return False
			
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

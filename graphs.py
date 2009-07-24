from random import random
from physics import Vec2d, linesegdist2
from graphutils import *

def free_path(p1, p2, obstacles, safe_distance = 0):
	for o in obstacles:
		if linesegdist2(p1, p2, o.position()) <= (o.radius+safe_distance)**2:
			return False
	return True
		
def prp(me, target_position, obstacles):
	safe_distance = me.radius+1
	start = Node()
	start.position = me.position()
	start.est_cost_there = me.position().distance_to(target_position)
	end = Node(0)
	end.position = target_position
	nodes = [start, end]
	if free_path(start.position, end.position, obstacles, safe_distance):
		start.connect(start.est_cost_there, end)
	else:
		while len(nodes) < 20:
			newnode = Node()
			newnode.position = me.position() + Vec2d((2*random()-1)*me.view_range, (2*random()-1)*me.view_range)
			connected = False
			for n in nodes:
				if free_path(newnode.position, n.position, obstacles, safe_distance):
					dist = newnode.position.distance_to(n.position)
					newnode.connect(dist, n)
					n.connect(dist, newnode)
					newnode.est_cost_there = newnode.position.distance_to(target_position) 
					connected = True
			if connected:
				nodes.append(newnode)
	
	result = shortest_path(start, end, nodes)
	if result.success:
		result.path = [nodes[i].position for i in result.indices]
	return result

def prp_turning(me, target_position, obstacles):
	safe_distance = me.radius+1
	pre_graph = []
	pre_graph.append((me.position(),[]))
	pre_graph.append((target_position,[]))
	
	if free_path(me.position(), target_position, obstacles, safe_distance):
		pre_graph[0][1].append(1)
	else:
		while len(nodes) < 20:
			newnode = (me.position() + Vec2d((2*random()-1)*me.view_range, (2*random()-1)*me.view_range),[])
			connected = False
			for node in pre_graph:
				if free_path(newnode[0], node[0], obstacles, safe_distance):
					node[1].append(len(pre_graph))
					connected = True
			if connected:
				pre_graph.append(newnode)
	
	
	result = shortest_path(start, end, nodes)
	if result.success:
		result.path = [nodes[i].position for i in result.indices]
	return result
	
if __name__ == "__main__":
	prm_turning((0,0), (10,10), ())

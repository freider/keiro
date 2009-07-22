from random import random
from physics import Vec2d, linesegdist2
from graphutils import *

def graph_connect(newnode, nodes, obstacles, safe_distance = 0):
	connected = False
	for n in nodes:
		collides = False
		for o in obstacles:
			if linesegdist2(newnode.position, n.position, o.position()) <= (o.radius+safe_distance)**2:
				collides = True
		if collides is False:
			connected = True
			dist = newnode.position.distance_to(n.position)
			newnode.connect(dist, n)
			n.connect(dist, newnode)
	return connected
			
def prm(me, target_position, obstacles):
	safe_distance = me.radius+1
	start = Node()
	start.position = me.position()
	start.est_cost_there = me.position().distance_to(target_position)
	end = Node(0)
	end.position = target_position
	nodes = [start, end]
	if graph_connect(start, (end,), obstacles, safe_distance) is False:
		while len(nodes) < 20:
			newnode = Node()
			newnode.position = me.position() + Vec2d(random()*150-75, random()*150-75)
			if graph_connect(newnode, nodes, obstacles, safe_distance) is True:
				newnode.est_cost_there = newnode.position.distance_to(target_position) 
				nodes.append(newnode)

	return (start, end, nodes)


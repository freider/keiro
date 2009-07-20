from astar import Node
from random import random
from physics import Vec2d

def linesegdist2(l1, l2, p):
	diff = l2-l1
	unit = diff.norm()
	seglen = diff.length()
	if abs((p-l1).dot(unit)) >= seglen or abs((p-l2).dot(unit)) >= seglen:
		return min(l1.distance_to2(p), l2.distance_to2(p))
	else:
		norm = Vec2d(-unit.y, unit.x)
		return norm.dot(p-l1)**2

def _graph_connect(nodes, obstacles, safe_distance = 0):
	for n in nodes:
		p1 = n.data
		for m in nodes:
			p2 = m.data
			good = True
			for o in obstacles:
				if linesegdist2(p1, p2, o.position()) <= (o.radius+safe_distance)**2:
					good = False
					break
			if good:
				n.edges.append((m, p1.distance_to(p2)))
				
def rand(me, target_position, obstacles):
	start = Node(me.position())
	end = Node(target_position)
	nodes = [start, end]
	for i in xrange(20):
		nodes.append(Node(me.position() + Vec2d(random()*150-75, random()*150-75)))
		
	_graph_connect(nodes, obstacles, me.radius)
	return (start, end)


from astar import Node
from random import random
from physics import Vec2d

def linesegdist2(l1, l2, p):
	diff = l2-l1
	unit = diff.norm()
	seglen = diff.lenght()
	if abs((p-l1).dot(unit)) >= seglen or abs((p-l2).dot(unit)) >= seglen:
		return min(l1.distance_to2(p), l2.distance_to2(p))
	else:
		norm = Vec2d(-unit.y, unit.x)
		return (norm*(p-l1))**2

def _graph_connect(nodes, obstacles):
	for n in nodes:
		p1 = n.data
		for m in nodes:
			p2 = m.data
			good = True
			for o in obstacles:
				if linesegdist2(p1.data, p1.data, o.position) <= o.radius**2:
					good = False
					break
			if good:
				n.edges.append((m, p1.distance_to(p2)))
				
def rand(my_position, target_position, obstacles):
	start = Node(my_position)
	end = Node(target_position)
	nodes = [start, end]
	for i in xrange(10):
		nodes.append(Node(Vec2d(random()*150-75, random()*150-75)))
		
	_graph_connect(nodes, obstacles)
	return (start, end)


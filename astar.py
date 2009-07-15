from heapq import heappush, heappop

class Node:
	__slots__ = ("edges", "data", "dist", "_best_expanded", "parent")
	def __init__(self, data = None):
		self.edges = []
		self.data = data
		self.dist = None
		self._best_expanded = None
		self.parent = None
	def __repr__(self):
		return str(self.data)
		
def astar(start, end, heuristic=lambda n:0):
	"""Finds shortest path using supplied heuristic"""
	pq = []
	start.dist = 0
	heappush(pq, (heuristic(start), start))
	
	while len(pq) != 0:
		heur, node = heappop(pq)
		if node == end:	break #done
		#has been expanded in a better state before
		if node._best_expanded is not None and node._best_expanded <= heur: continue
		node._best_expanded = heur
		print "expanding " + str(node.data)
		for child, cost in node.edges:
			ndist = node.dist+cost
			if child.dist is None or ndist < child.dist:
				child.dist = ndist
				child.parent = node
				heappush(pq, (ndist+heuristic(child), child))
	if end.parent is None:
		return False
	else:
		node = end
		res = []
		while node is not None:
			res.append(node)
			node = node.parent
		res.reverse()
		return res

		
if __name__ == "__main__":
	def tc1():
		a = Node(("a", 6))
		b = Node(("b", 5))
		c = Node(("c", 0))
		d = Node(("d", 0))
		a.edges.append((c, 5))
		a.edges.append((b, 1))
		b.edges.append((c, 1))
		c.edges.append((d, 4))
		res = astar(a, d, lambda n:0)
		print res[-1].dist, res

	def tc2():
		import graphs
		from physics import Vec2d
		start, end = graphs.rand(Vec2d(-100,100), Vec2d(100,100), ())
		for i in start.edges:
			if i[0] == end:
				start.edges.remove(i)
				break
		print astar(start, end, lambda n:n.data.distance_to(Vec2d(100,100)))
	
	tc2()
			

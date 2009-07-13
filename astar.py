from heapq import heappush, heappop

class Node:
	def __init__(self, data = None):
		self.edges = []
		self.data = data
		self.dist = None
		self.parent = None
	def __repr__(self):
		return repr(self.data)
		
def dijkstra(start, end):
	"""Finds shortest path"""
	pq = []
	heappush(pq, (0, start, None)) #h, g, node, parent
	
	while len(pq) != 0:
		dist, node, parent = heappop(pq)
		if node.parent is not None: continue #visited before
		node.parent = parent
		if node == end:	break #done
		node.parent = parent
		for child, cost in node.edges:
			nc = dist+cost
			if child.dist is None or nc < child.dist:
				child.dist = nc
				heappush(pq, (nc, child, node))
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
	start = Node("Start")
	end = Node("End")
	m1 = Node("M1")
	m2 = Node("M2")
	start.edges.append((m1, 4))
	start.edges.append((m2, 4))
	m1.edges.append((end, 10))
	m2.edges.append((end, 9))
	print dijkstra(start, end)
			

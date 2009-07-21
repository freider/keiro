#include "graphs.h"
#include <cstdio>

int main(void){
	Node a(0, 6), b(1,5), c(2, 0), d(3, 0);
	a.edges.push_back(Edge(10, d));
	a.edges.push_back(Edge(5, c));
	a.edges.push_back(Edge(1, b));
	b.edges.push_back(Edge(1, c));
	c.edges.push_back(Edge(4, d));
	Path res = shortest_path(a, d);
	printf("%d\n", res.total_cost);
}

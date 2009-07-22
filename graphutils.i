/* graphs.i */
%module graphutils
%include "std_vector.i"
%{
#include "graphutils.h"
%}

class Node;

struct Edge{
	float cost;
	Node *to;
	Edge(float _cost, Node& _to);
};

struct Path{
	bool success;
	int total_cost;
	std::vector<int> indices;
};

class Node{
public:
	std::vector<Edge> edges;
	float cost_here;
	int index;
	Node(int _index, float _est_cost_there);
};

Path shortest_path(Node &start, Node &goal);

/* graphutils.i */
%module graphutils
%include "std_vector.i"
%{
#include "graphutils.h"
%}
%template(int_vector) std::vector<int>; 
%template(node_vector) std::vector<Node*>; 

struct Path{
	bool success;
	float total_cost;
	std::vector<int> indices;
};

class Node{
public:
	float cost_here;
	float est_cost_there;
	Node(float _est_cost_there = 0.0);
	void connect(float cost, Node &n);
};

Path shortest_path(Node &start, Node &goal, const std::vector<Node*> &nodes = std::vector<Node*>());

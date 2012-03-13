#include <vector>
#include <queue>
#include <limits>
#include <algorithm>

class Node;

struct Edge{
	float cost;
	Node *to;
	Edge(float _cost, Node& _to):cost(_cost), to(&_to){}
};

struct Path{
	bool success;
	float total_cost;
	std::vector<int> indices;
};

class Node{
public:
	std::vector<Edge> edges;
	float cost_here;
	float est_cost_there;
	float cost_through_here() {
		return cost_here + est_cost_there;
	}
	float _best_expanded; //used internally by A*
	Node *parent;
	int index;
	Node(float _est_cost_there = 0.0): //default as dijkstra
			cost_here(std::numeric_limits<float>::max()),
			est_cost_there(_est_cost_there),
			_best_expanded(std::numeric_limits<float>::max()),
			parent(NULL),
			index(-1)
			{}
	void connect(float cost, Node &n){
		edges.push_back(Edge(cost, n));
	}
};

typedef std::pair<float,Node*> pqnode;

//A* shortest path
Path shortest_path(Node &start, Node &goal, const std::vector<Node*> &nodes = std::vector<Node*>());

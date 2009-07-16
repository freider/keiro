#include <vector>
#include <priority_queue>

class Node;

struct Edge{
	float cost;
	Node *to;
};

struct Path{
	bool success;
	int total_cost;
	vector<int> indices;
};

class Node{
public:
	std::vector<Edge> edges;
	float cost_here;
	float est_cost_there;
	float cost_through_here(){return cost_here + est_cost_there}
	int index;
};

typedef pqnode pair<float,Node*>;

//A* shortest path
Path shortest_path(Node *start, Node *goal){
	Path result;
	priority_queue<pqnode> pq;
	
	
	return result;
}


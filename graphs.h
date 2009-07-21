#include <vector>
#include <queue>

class Node;

struct Edge{
	float cost;
	Node *to;
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
	float est_cost_there;
	float cost_through_here(){return cost_here + est_cost_there;}
	int index;
};

typedef std::pair<float,Node*> pqnode;

//A* shortest path
Path shortest_path(Node *start, Node *goal){
	Path result;
	std::priority_queue<pqnode> pq;
	pq.push(pqnode(start.est_cost_there,start));
	
	return result;
}


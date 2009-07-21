#include <vector>
#include <queue>
#include <limits>

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
	float _best_expanded; //used internally by A*
	Node *parent;
	int index;
	Node(int _index):cost_here(std::numeric_limits<float>::min()),
			est_cost_there(0), //default as a dijkstra
			_best_expanded(std::numeric_limits<float>::max()),
			index(_index),
			parent(NULL){}
};

typedef std::pair<float,Node*> pqnode;

//A* shortest path
Path shortest_path(Node *start, Node *goal){
	Path result;
	std::priority_queue<pqnode> pq;
	start->cost_here = 0;
	pq.push(pqnode(start->cost_through_here(),start));
	while(!pq.empty()){
		pqnode n = pq.top();
		pq.pop();
		Node &node = *n.second;
		if(&node == goal)
			break;
		if(n.first >= node._best_expanded)
			continue; //we have done better		
		for(size_t i = 0; i<node.edges.size(); i++){
			float newcost = node.cost_here + node.edges[i].cost;
			Node &to = *node.edges[i].to;
			if(newcost < to.cost_here){
				to.cost_here = newcost;			
				to.parent = &node;
			}
		}
	}
	if(goal->parent == NULL){
		result.success = false;
		return result;
	} else {
		result.success = true;
		result.total_cost = 0;
		Node *last = goal;
		while(last != NULL){
			result.indices.push_back(last->index);
			last = last->parent;
		}
	}
	return result;
}


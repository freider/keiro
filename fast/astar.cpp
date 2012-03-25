#include "astar.hpp"
#include <cstdio>

Path shortest_path(Node &start, Node &goal, const std::vector<Node*> &nodes){
	bool return_path = (nodes.size() != 0);
	if(return_path){
		//mark nodes with indices
		for(int i = 0; i<(int)nodes.size(); ++i){
			nodes[i]->index = i;		
		}
	}
	Path result;
	std::priority_queue<pqnode, std::vector<pqnode>, std::greater<pqnode> > pq;
	start.cost_here = 0;
	pq.push(pqnode(start.cost_through_here(), &start));
	while(!pq.empty()){
		pqnode n = pq.top();
		pq.pop();
		Node &node = *n.second;
		if(&node == &goal) 
			break; //this is only valid if the heuristic is consistent
		if(n.first >= node._best_expanded)
			continue; //we have done better
		node._best_expanded = n.first;
		//printf("expanding %d\n", node.index);
		for(size_t i = 0; i<node.edges.size(); i++){
			float newcost = node.cost_here + node.edges[i].cost;
			Node &to = *node.edges[i].to;
			if(newcost < to.cost_here){
				to.cost_here = newcost;			
				to.parent = &node;
				pq.push(pqnode(to.cost_through_here(), &to));
				//printf("	adding %d\n", to.index);
			}
		}
	}
	if(goal.parent == NULL && &goal != &start){
		result.success = false;
		return result;
	} else {
		result.success = true;
		result.total_cost = goal.cost_here;
		if(return_path){
			Node *last = &goal;
			while(last != NULL){
				result.indices.push_back(last->index);
				last = last->parent;
			}
			std::reverse(result.indices.begin(), result.indices.end());
		}
	}
	return result;
}


int main(void){
	Node a(6), b(5), c(0), d(0);
	a.connect(10, d);
	a.connect(5, c);
	a.connect(1, b);
	b.connect(1, c);
	c.connect(4, d);
	Path res = shortest_path(a, d);
	printf("%lf\n", res.total_cost);
}

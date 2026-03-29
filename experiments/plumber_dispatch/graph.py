from typing import Any, Optional


class Node:
    def __init__(self, data: Any):
        self.data: Any = data
        self.outgoing: dict['Node', float] = {}
        self.incoming: dict['Node', float] = {}
    
    def add_edge(self, target: 'Node', weight: float = 1.0):
        self.outgoing[target] = weight
        target.incoming[self] = weight
    
    def remove_edge(self, target: 'Node'):
        if target in self.outgoing:
            del self.outgoing[target]
            del target.incoming[self]


class Graph:
    def __init__(self):
        self.nodes: dict[Any, Node] = {}
        self.edges: set[tuple[Any, Any]] = set()
    
    def add_node(self, data: Any) -> Node:
        if data not in self.nodes:
            self.nodes[data] = Node(data)
        return self.nodes[data]
    
    def get_node(self, data: Any) -> Optional[Node]:
        return self.nodes.get(data)
    
    def add_edge(self, from_data: Any, to_data: Any, weight: float = 1.0):
        from_node = self.add_node(from_data)
        to_node = self.add_node(to_data)
        from_node.add_edge(to_node, weight)
        self.edges.add((from_data, to_data))
    
    def remove_edge(self, from_data: Any, to_data: Any):
        from_node = self.get_node(from_data)
        to_node = self.get_node(to_data)
        if from_node and to_node:
            from_node.remove_edge(to_node)
    
    def has_edge(self, from_data: Any, to_data: Any) -> bool:
        from_node = self.get_node(from_data)
        to_node = self.get_node(to_data)
        return from_node is not None and to_node is not None and to_node in from_node.outgoing
    
    def get_neighbors(self, data: Any) -> dict[Any, float]:
        node = self.get_node(data)
        if not node:
            return {}
        return {neighbor.data: weight for neighbor, weight in node.outgoing.items()}
    
    def draw(self):
        if not self.nodes:
            print("Empty graph")
            return
            
        for node_data, node in self.nodes.items():
            print(f"*({node_data})")
            for neighbor, weight in node.outgoing.items():
                weight_str = f" ({weight})" if weight != 1.0 else ""
                print(f"  └──> {neighbor.data}{weight_str}")
            if not node.outgoing:
                print("  └──> (no outgoing edges)")


if __name__ == "__main__":
    graph = Graph()
    
    # Add edges (nodes are created automatically)
    graph.add_edge('A', 'B')
    graph.add_edge('A', 'C')
    graph.add_edge('B', 'C')
    graph.add_edge('B', 'D')
    graph.add_edge('C', 'D')
    graph.add_edge('D', 'C')
    graph.add_edge('E', 'F', 2.5)  # With custom weight
    graph.add_edge('F', 'C')
    
    # Draw the graph
    print("Graph structure:")
    graph.draw()
    
    # Example queries
    print(f"\nNeighbors of 'A': {graph.get_neighbors('A')}")
    print(f"Has edge A->B: {graph.has_edge('A', 'B')}")
    print(f"Has edge B->A: {graph.has_edge('B', 'A')}")
import networkx as nx
import numpy as np
from typing import Set, Tuple, Dict, Optional

class VisibilityOracle:
    """
    Determines the visibility of edges based on the observer's position in the graph.
    """
    def __init__(self, policy: str = "1-hop"):
        self.policy = policy

    def is_visible(self, graph: nx.Graph, observer: int, edge: Tuple[int, int]) -> bool:
        """
        Checks if an edge (u, v) is visible to the observer.
        """
        u, v = edge
        
        if self.policy == "1-hop":
            # Observer sees edge (u, v) if they are adjacent to u or v.
            if observer == u or observer == v:
                return True
            if graph.has_edge(observer, u) or graph.has_edge(observer, v):
                return True
            return False
            
        elif self.policy == "2-hop":
            # Observer sees edge (u, v) if u and v are within 2 hops?
            # Usually: Induced subgraph on {x | dist(observer, x) <= 2}
            # Or: Edges (u, v) where at least one endpoint is within distance 1?
            # Let's define: Visible if BOTH u and v are within distance 2 of observer.
            
            # Optimization: Precompute distances? No, too slow.
            # Check distance on the fly or use BFS from observer.
            # Since we usually call get_visible_subgraph, we'll implement the logic there efficiently.
            # Here, for single edge check (slow):
            try:
                dist_u = nx.shortest_path_length(graph, observer, u)
                dist_v = nx.shortest_path_length(graph, observer, v)
                return dist_u <= 2 and dist_v <= 2
            except nx.NetworkXNoPath:
                return False
            
        elif self.policy == "global":
            return True
            
        return False

class SocialGraph:
    """
    Wrapper for the social network graph with visibility constraints.
    """
    def __init__(self, data_path: Optional[str] = None, public_fraction: float = 0.0, public_strategy: str = "degree_top_k"):
        self.graph = nx.Graph()
        self.public_nodes = set()
        self.public_fraction = public_fraction
        self.public_strategy = public_strategy
        
        if data_path:
            self.load_data(data_path)
            
    def load_data(self, path: str):
        # Load from edge list
        self.graph = nx.read_edgelist(path, nodetype=int)
        self._select_public_nodes()
        
    def _select_public_nodes(self):
        nodes = list(self.graph.nodes())
        num_public = int(len(nodes) * self.public_fraction)
        
        if num_public == 0:
            self.public_nodes = set()
            return

        if self.public_strategy == "random":
            self.public_nodes = set(np.random.choice(nodes, num_public, replace=False))
            
        elif self.public_strategy == "degree_top_k":
            # Select top k nodes by degree
            degree_dict = dict(self.graph.degree())
            sorted_nodes = sorted(degree_dict.items(), key=lambda item: item[1], reverse=True)
            top_k_nodes = [node for node, degree in sorted_nodes[:num_public]]
            self.public_nodes = set(top_k_nodes)
            
        elif self.public_strategy == "degree_probabilistic":
            # Probability proportional to degree
            degrees = np.array([self.graph.degree(n) for n in nodes])
            total_degree = degrees.sum()
            if total_degree > 0:
                probs = degrees / total_degree
                self.public_nodes = set(np.random.choice(nodes, num_public, replace=False, p=probs))
            else:
                self.public_nodes = set(np.random.choice(nodes, num_public, replace=False))

        
    def is_public(self, node: int) -> bool:
        return node in self.public_nodes
        
    def get_visible_subgraph(self, observer: int, oracle: VisibilityOracle) -> nx.Graph:
        """
        Returns a subgraph containing only edges visible to the observer.
        """
        if oracle.policy == "1-hop":
            subgraph = nx.Graph()
            # Edges incident to observer
            for nbr in self.graph.neighbors(observer):
                subgraph.add_edge(observer, nbr)
                # Edges incident to neighbors
                for nbr_of_nbr in self.graph.neighbors(nbr):
                    subgraph.add_edge(nbr, nbr_of_nbr)
            return subgraph
            
        elif oracle.policy == "2-hop":
            # BFS to depth 2
            nodes_at_dist_0 = {observer}
            nodes_at_dist_1 = set(self.graph.neighbors(observer))
            nodes_at_dist_2 = set()
            for n1 in nodes_at_dist_1:
                for n2 in self.graph.neighbors(n1):
                    if n2 not in nodes_at_dist_1 and n2 != observer:
                        nodes_at_dist_2.add(n2)
            
            visible_nodes = nodes_at_dist_0 | nodes_at_dist_1 | nodes_at_dist_2
            return self.graph.subgraph(visible_nodes).copy()
            
        # Fallback
        subgraph = nx.Graph()
        return subgraph

    def get_global_graph(self):
        return self.graph

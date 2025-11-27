import numpy as np
import networkx as nx

def laplace_mechanism(true_value: float, sensitivity: float, epsilon: float) -> float:
    """
    Adds Laplace noise to the true value.
    """
    scale = sensitivity / epsilon
    noise = np.random.laplace(0, scale)
    return true_value + noise

def geometric_mechanism(true_value: int, sensitivity: float, epsilon: float) -> int:
    """
    Discrete Laplace (Geometric) mechanism for integer outputs.
    """
    # For simplicity using rounded Laplace or numpy's geometric if available/appropriate.
    # Standard geometric mechanism: P(x) \propto exp(-epsilon * |x| / sensitivity)
    # Here we approximate with rounded Laplace for simplicity in this prototype, 
    # or implement properly if needed.
    scale = sensitivity / epsilon
    noise = np.random.laplace(0, scale)
    return int(round(true_value + noise))

def perform_random_walk(graph: nx.Graph, start_node: int, walk_length: int) -> list:
    """
    Performs a random walk starting from start_node.
    """
    path = [start_node]
    current = start_node
    for _ in range(walk_length):
        neighbors = list(graph.neighbors(current))
        if not neighbors:
            break
        current = np.random.choice(neighbors)
        path.append(current)
    return path

def sample_power_law_subgraph(graph: nx.Graph, size: int) -> nx.Graph:
    """
    Samples a subgraph using Random Walk to preserve power-law properties roughly.
    """
    start_node = np.random.choice(graph.nodes())
    nodes_to_keep = set([start_node])
    
    # Simple BFS or RW expansion until size is met
    queue = [start_node]
    while len(nodes_to_keep) < size and queue:
        current = queue.pop(0)
        neighbors = list(graph.neighbors(current))
        np.random.shuffle(neighbors)
        for n in neighbors:
            if n not in nodes_to_keep:
                nodes_to_keep.add(n)
                queue.append(n)
                if len(nodes_to_keep) >= size:
                    break
                    
    return graph.subgraph(nodes_to_keep).copy()

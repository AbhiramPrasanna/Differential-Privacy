import numpy as np
import networkx as nx
from typing import Dict, List, Callable, Tuple
from .model import SocialGraph, VisibilityOracle
from .utils import laplace_mechanism
import math

class GraphDPAlgorithms:
    def __init__(self, graph: SocialGraph, oracle: VisibilityOracle):
        self.graph = graph
        self.oracle = oracle

    def _aggregate_local_queries(self, query_func: Callable[[nx.Graph, int], float], epsilon: float, sensitivity: float) -> float:
        """
        Generic aggregator for local queries.
        """
        total_estimate = 0.0
        nodes = list(self.graph.graph.nodes())
        
        for node in nodes:
            # 1. Get visible subgraph
            subgraph = self.graph.get_visible_subgraph(node, self.oracle)
            
            # 2. Compute local function
            true_val = query_func(subgraph, node)
            
            # 3. Add noise (ONLY if node is PRIVATE)
            if self.graph.is_public(node):
                noisy_val = true_val
            else:
                noisy_val = laplace_mechanism(true_val, sensitivity, epsilon)
            
            total_estimate += noisy_val
            
        return total_estimate

    def edge_count(self, epsilon: float) -> Tuple[float, float]:
        """
        Estimates total edge count.
        Returns (estimate, sensitivity).
        """
        sensitivity = 1.0
        
        def local_degree(subgraph: nx.Graph, node: int) -> float:
            return float(subgraph.degree(node)) if node in subgraph else 0.0

        total_degree_noisy = self._aggregate_local_queries(local_degree, epsilon, sensitivity)
        return total_degree_noisy / 2.0, sensitivity

    def degree_histogram(self, epsilon: float, max_degree: int = 50) -> Tuple[List[float], float]:
        """
        Estimates degree histogram.
        Returns (histogram, sensitivity).
        """
        # Simplified: Each user reports their degree (clamped).
        # We build a histogram from these noisy degrees.
        # Sensitivity of reporting degree is 1.
        sensitivity = 1.0
        
        noisy_degrees = []
        nodes = list(self.graph.graph.nodes())
        
        for node in nodes:
            # 1. Get visible subgraph
            subgraph = self.graph.get_visible_subgraph(node, self.oracle)
            
            # 2. Compute local degree
            true_d = subgraph.degree(node) if node in subgraph else 0
            true_d = min(true_d, max_degree)
            
            # 3. Add noise
            if self.graph.is_public(node):
                noisy_d = true_d
            else:
                noisy_d = laplace_mechanism(true_d, sensitivity, epsilon)
            
            noisy_degrees.append(noisy_d)
            
        # Build histogram
        hist, _ = np.histogram(noisy_degrees, bins=range(max_degree + 2))
        return hist.tolist(), sensitivity

    def k_star_count(self, k: int, epsilon: float) -> Tuple[float, float]:
        """
        Estimates number of k-stars.
        Returns (estimate, sensitivity).
        """
        D_max = 50 
        sensitivity = math.comb(D_max - 1, k - 1)
        
        def local_k_star(subgraph: nx.Graph, node: int) -> float:
            d = subgraph.degree(node) if node in subgraph else 0
            
            # Optimization: No clipping for public nodes
            if not self.graph.is_public(node):
                d = min(d, D_max)
                
            if d < k:
                return 0.0
            return math.comb(d, k)

        total_k_stars = self._aggregate_local_queries(local_k_star, epsilon, sensitivity)
        return total_k_stars, sensitivity

    def k_star_count_smooth(self, k: int, epsilon: float) -> Tuple[float, float]:
        """
        Estimates k-stars using Instance-Specific Sensitivity.
        Sensitivity for node u is comb(degree(u), k-1).
        For k=2, Sensitivity = degree(u).
        """
        import math
        
        def local_k_star_smooth(subgraph: nx.Graph, node: int) -> float:
            d = subgraph.degree(node) if node in subgraph else 0
            # No clipping
            if d < k:
                return 0.0
            return math.comb(d, k)

        total_estimate = 0.0
        nodes = list(self.graph.graph.nodes())
        avg_sensitivity = 0.0
        
        for node in nodes:
            subgraph = self.graph.get_visible_subgraph(node, self.oracle)
            true_val = local_k_star_smooth(subgraph, node)
            
            # Calculate Instance-Specific Sensitivity
            d = subgraph.degree(node) if node in subgraph else 0
            if d < k - 1:
                local_sens = 1.0 # Min sensitivity
            else:
                local_sens = float(math.comb(d, k - 1))
            
            local_sens = max(1.0, local_sens)
            avg_sensitivity += local_sens
            
            if self.graph.is_public(node):
                noisy_val = true_val
            else:
                noisy_val = laplace_mechanism(true_val, local_sens, epsilon)
            
            total_estimate += noisy_val
            
        return total_estimate, avg_sensitivity / len(nodes)

    def triangle_count_smooth(self, epsilon: float) -> Tuple[float, float]:
        """
        Estimates triangles using a "Smooth Sensitivity"-like approach for LDP.
        Instead of clipping at D_max (Global Sensitivity), we scale noise 
        based on the user's ACTUAL local sensitivity.
        """
        
        def local_triangles_smooth(subgraph: nx.Graph, node: int) -> float:
            if node not in subgraph:
                return 0.0
            
            neighbors = list(subgraph.neighbors(node))
            # NO CLIPPING! We use the full degree.
            
            tri_count = 0
            # Calculate local triangles
            for i in range(len(neighbors)):
                for j in range(i + 1, len(neighbors)):
                    u = neighbors[i]
                    v = neighbors[j]
                    if subgraph.has_edge(u, v):
                        tri_count += 1
            
            return float(tri_count)

        # Aggregation with Instance-Specific Noise
        total_estimate = 0.0
        nodes = list(self.graph.graph.nodes())
        avg_sensitivity = 0.0
        
        for node in nodes:
            subgraph = self.graph.get_visible_subgraph(node, self.oracle)
            true_val = local_triangles_smooth(subgraph, node)
            
            # Calculate Instance-Specific Sensitivity
            neighbors = list(subgraph.neighbors(node))
            if not neighbors:
                local_sens = 1.0
            else:
                max_common = 0
                for v in neighbors:
                    v_neighbors = set(subgraph.neighbors(v))
                    common = 0
                    for w in neighbors:
                        if w in v_neighbors:
                            common += 1
                    if common > max_common:
                        max_common = common
                local_sens = float(max_common)
            
            # Ensure sensitivity is at least 1 to avoid div by zero
            local_sens = max(1.0, local_sens)
            avg_sensitivity += local_sens
            
            # Add noise scaled by LOCAL sensitivity
            if self.graph.is_public(node):
                noisy_val = true_val
            else:
                noisy_val = laplace_mechanism(true_val, local_sens, epsilon)
            
            total_estimate += noisy_val
            
        return total_estimate / 3.0, avg_sensitivity / len(nodes)

    def triangle_count(self, epsilon: float) -> Tuple[float, float]:
        """
        Estimates number of triangles.
        Returns (estimate, sensitivity).
        """
        D_max = 50
        sensitivity = D_max 
        
        def local_triangles(subgraph: nx.Graph, node: int) -> float:
            if node not in subgraph:
                return 0.0
            
            neighbors = list(subgraph.neighbors(node))
            
            if not self.graph.is_public(node):
                neighbors = neighbors[:D_max]
            
            tri_count = 0
            # Simple iteration
            for i in range(len(neighbors)):
                for j in range(i + 1, len(neighbors)):
                    u = neighbors[i]
                    v = neighbors[j]
                    if subgraph.has_edge(u, v):
                        tri_count += 1
            return float(tri_count)

        total_triangles = self._aggregate_local_queries(local_triangles, epsilon, sensitivity)
        return total_triangles / 3.0, sensitivity

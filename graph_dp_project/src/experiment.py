import sys
import os
import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Add src and libs to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'libs'))

from src.model import SocialGraph, VisibilityOracle
from src.algorithms import GraphDPAlgorithms
from src.utils import sample_power_law_subgraph

def run_experiments():
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'facebook_combined.txt')
    
    graphs_to_test = []
    
    # 1. Facebook SNAP (Power Law)
    if os.path.exists(data_path):
        print("Loading Facebook graph...")
        full_graph = SocialGraph(data_path, public_fraction=0.2, public_strategy="degree_top_k")
        print("Sampling subgraph...")
        sampled_nx_graph = sample_power_law_subgraph(full_graph.graph, size=1000)
        sampled_graph = SocialGraph(public_fraction=0.2, public_strategy="degree_top_k")
        sampled_graph.graph = sampled_nx_graph
        sampled_graph.public_nodes = {n for n in sampled_nx_graph.nodes() if n in full_graph.public_nodes}
        graphs_to_test.append(("Facebook_Sample", sampled_graph))
    else:
        print(f"Data file not found at {data_path}. Please run download_data.py first.")
        return

    epsilons = [0.1, 0.5, 1.0, 2.0, 5.0]
    results = []

    for graph_name, graph_obj in graphs_to_test:
        print(f"\nRunning experiments on {graph_name}...")
        oracle = VisibilityOracle(policy="2-hop")
        dp_algo = GraphDPAlgorithms(graph_obj, oracle)
        
        # Ground Truth
        true_edges = graph_obj.graph.number_of_edges()
        true_triangles = sum(nx.triangles(graph_obj.graph).values()) / 3
        
        # True k-stars (k=2)
        # k=2 stars = sum( (d choose 2) )
        import math
        true_k2_stars = sum([math.comb(d, 2) for n, d in graph_obj.graph.degree() if d >= 2])
        
        print(f"Ground Truth - Edges: {true_edges}, Triangles: {true_triangles}, 2-Stars: {true_k2_stars}")

        for eps in epsilons:
            print(f"  Running for epsilon={eps}...")
            
            # Edge Count
            est_edges, sens_edges = dp_algo.edge_count(epsilon=eps)
            edge_error = abs(est_edges - true_edges) / true_edges if true_edges > 0 else 0
            
            # Triangle Count (Clipped)
            est_triangles, sens_tri = dp_algo.triangle_count(epsilon=eps)
            tri_error = abs(est_triangles - true_triangles) / true_triangles if true_triangles > 0 else 0
            
            # Triangle Count (Smooth / Instance-Specific)
            est_tri_smooth, sens_tri_smooth = dp_algo.triangle_count_smooth(epsilon=eps)
            tri_smooth_error = abs(est_tri_smooth - true_triangles) / true_triangles if true_triangles > 0 else 0
            
            # k-Star Count (k=2) (Clipped)
            est_k2, sens_k2 = dp_algo.k_star_count(k=2, epsilon=eps)
            k2_error = abs(est_k2 - true_k2_stars) / true_k2_stars if true_k2_stars > 0 else 0

            # k-Star Count (k=2) (Smooth)
            est_k2_smooth, sens_k2_smooth = dp_algo.k_star_count_smooth(k=2, epsilon=eps)
            k2_smooth_error = abs(est_k2_smooth - true_k2_stars) / true_k2_stars if true_k2_stars > 0 else 0
            
            results.append({
                "graph": graph_name,
                "epsilon": eps,
                "metric": "EdgeCount",
                "true_val": true_edges,
                "est_val": est_edges,
                "rel_error": edge_error,
                "sensitivity": sens_edges
            })
            results.append({
                "graph": graph_name,
                "epsilon": eps,
                "metric": "TriangleCount_Clipped",
                "true_val": true_triangles,
                "est_val": est_triangles,
                "rel_error": tri_error,
                "sensitivity": sens_tri
            })
            results.append({
                "graph": graph_name,
                "epsilon": eps,
                "metric": "TriangleCount_Smooth",
                "true_val": true_triangles,
                "est_val": est_tri_smooth,
                "rel_error": tri_smooth_error,
                "sensitivity": sens_tri_smooth
            })
            results.append({
                "graph": graph_name,
                "epsilon": eps,
                "metric": "2-StarCount_Clipped",
                "true_val": true_k2_stars,
                "est_val": est_k2,
                "rel_error": k2_error,
                "sensitivity": sens_k2
            })
            results.append({
                "graph": graph_name,
                "epsilon": eps,
                "metric": "2-StarCount_Smooth",
                "true_val": true_k2_stars,
                "est_val": est_k2_smooth,
                "rel_error": k2_smooth_error,
                "sensitivity": sens_k2_smooth
            })

    df = pd.DataFrame(results)
    print("\nResults:")
    print(df)
    
    # Save results
    output_csv = os.path.join(os.path.dirname(__file__), '..', 'paper', 'results_comprehensive.csv')
    df.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")

if __name__ == "__main__":
    run_experiments()

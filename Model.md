# Visibility-Aware Edge Local Differential Privacy (VA-Edge-LDP)

A comprehensive framework for privacy-preserving graph analytics on social networks using **TRUE Edge-Level Local Differential Privacy** with visibility-aware noise optimization.

---

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Dataset: SNAP Facebook](#dataset-snap-facebook)
4. [The Binary Visibility Model](#the-binary-visibility-model)
5. [Edge Classification Algorithm](#edge-classification-algorithm)
6. [TRUE Edge-LDP Algorithms](#true-edge-ldp-algorithms)
7. [Installation & Usage](#installation--usage)
8. [API Reference](#api-reference)
9. [Mathematical Foundations](#mathematical-foundations)
10. [Experimental Results](#experimental-results)

---

## Overview

### What is VA-Edge-LDP?

VA-Edge-LDP is a privacy framework that enables **graph analytics** (edge counting, max degree, triangles, k-stars) while providing **rigorous differential privacy guarantees** at the edge level.

### The Core Innovation

Not all edges in a social network need the same privacy protection:

| Edge Type | Example | Privacy Need |
|-----------|---------|--------------|
| **PUBLIC** | Celebrity connections | None (publicly visible) |
| **PRIVATE** | Private user friendships | Full ε-LDP protection |

By classifying edges and applying noise only where needed, we achieve **better accuracy** while maintaining **full privacy** for sensitive connections.

```
┌─────────────────────────────────────────────────────────────────┐
│                    VA-Edge-LDP ADVANTAGE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Standard LDP:     ALL edges → Noise → High variance           │
│                                                                 │
│  VA-Edge-LDP:      PUBLIC edges → No noise → Exact values      │
│                    PRIVATE edges → ε-LDP → Full protection     │
│                                                                 │
│  Result: ~20% less noise with SAME privacy for private edges   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Features

- ✅ **TRUE Local DP**: No trusted curator - each edge perturbs locally
- ✅ **Edge-Level Privacy**: Granular per-edge protection (not per-node)
- ✅ **Binary Visibility Model**: Clean PUBLIC/PRIVATE classification
- ✅ **Power-Law Aware**: Leverages social network degree distribution
- ✅ **Two-Round Protocol**: Enables subgraph counting under Edge-LDP
- ✅ **SNAP Integration**: Works with Stanford Network Analysis datasets

---

## Dataset: SNAP Facebook

### Source

The framework uses the **Facebook ego-network dataset** from Stanford's SNAP project:

```
Source:    Stanford Network Analysis Project (SNAP)
URL:       https://snap.stanford.edu/data/facebook_combined.txt.gz
File:      data/facebook_combined.txt
Reference: J. McAuley and J. Leskovec (2012)
```

### Statistics

| Property | Value |
|----------|-------|
| Nodes | 4,039 (Facebook users) |
| Edges | 88,234 (friendship connections) |
| Average Degree | 43.69 |
| Max Degree | 1,045 |
| Min Degree | 1 |

### Power-Law Distribution

Social networks follow a **power-law degree distribution**:

$$P(k) \propto k^{-\alpha}, \quad \text{where } \alpha \approx 2.5$$

```
                  DEGREE DISTRIBUTION
                  
  Number of
  Users (log)
      │
  10³ │██
      │████
  10² │████████
      │████████████████
  10¹ │████████████████████████████████████████████████
      └────────────────────────────────────────────────▶
           1      10       100      1000     Degree
           
      └──────────────────┘  └──────────────────────────┘
        MANY users with         FEW users with
        few friends             many friends
        (private users)         (influencers/hubs)
```

### Supported Datasets

| Dataset | Description | Nodes | Edges |
|---------|-------------|-------|-------|
| `facebook` | Facebook social network | 4,039 | 88,234 |
| `twitter` | Twitter social network | - | - |
| `email` | Enron email network | - | - |
| `ca-grqc` | arXiv GR collaboration | - | - |
| `ca-hepth` | arXiv HEP-TH collaboration | - | - |

---

## The Binary Visibility Model

### Visibility Classes

Each edge is classified into exactly one of two classes:

| Class | Noise Multiplier | Description |
|-------|------------------|-------------|
| **PUBLIC** | 0.0 | No privacy needed → No noise |
| **PRIVATE** | 1.0 | Full privacy → Full ε-LDP noise |

### Real-World Intuition

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOCIAL NETWORK REALITY                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  High-Degree Users (Influencers/Celebrities):                  │
│  • Connections are often PUBLIC knowledge                      │
│  • Media reports on their relationships                        │
│  • Profile visibility set to "public"                          │
│                                                                 │
│  Low-Degree Users (Private Individuals):                       │
│  • Connections are PRIVATE                                     │
│  • Profile set to "friends only"                               │
│  • Privacy is expected and valued                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Privacy Guarantee

For neighboring graphs G, G' differing in one PRIVATE edge e:

$$\Pr[M(G) \in S] \leq e^{\varepsilon} \cdot \Pr[M(G') \in S]$$

- **PUBLIC edges**: No guarantee needed (publicly known)
- **PRIVATE edges**: Full ε-LDP guarantee

---

## Edge Classification Algorithm

### The Key Insight

Edges connected to **high-degree nodes** are more likely to be PUBLIC because high-degree users (influencers) have visible connections.

### Algorithm Overview

```
┌─────────────────────────────────────────────────────────────────┐
│               EDGE CLASSIFICATION ALGORITHM                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INPUT: Graph G, target public fraction f_pub (e.g., 0.2)      │
│  OUTPUT: visibility[(u,v)] ∈ {PUBLIC, PRIVATE} for each edge   │
│                                                                 │
│  1. Compute degrees: d[v] for all nodes v                      │
│  2. Compute d_max = max degree in graph                        │
│                                                                 │
│  3. For each edge (u, v):                                      │
│                                                                 │
│     a. Compute visibility score (0 to 1):                      │
│                                                                 │
│        score = [log(1 + d_u) + log(1 + d_v)]                   │
│                ─────────────────────────────                    │
│                    2 × log(1 + d_max)                          │
│                                                                 │
│     b. Convert to probability:                                 │
│                                                                 │
│        P(PUBLIC) = min(1.0, score² × f_pub × 3)                │
│                                                                 │
│     c. Random assignment:                                      │
│                                                                 │
│        if random() < P(PUBLIC):                                │
│            visibility[(u,v)] = PUBLIC                          │
│        else:                                                   │
│            visibility[(u,v)] = PRIVATE                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Why This Formula?

| Component | Purpose |
|-----------|---------|
| `log(1 + d)` | Handles heavy-tailed power-law distribution |
| Sum of both degrees | Both endpoints matter for visibility |
| Normalize by `d_max` | Scale to [0, 1] range |
| `score²` (quadratic) | Concentrate PUBLIC on highest-degree edges |
| `× f_pub × 3` | Calibrate to achieve target public fraction |

### Concrete Examples

| Edge | Degrees | Score | P(PUBLIC) | Typical Result |
|------|---------|-------|-----------|----------------|
| Hub ↔ Hub | (347, 253) | 0.82 | 40% | Often PUBLIC |
| Hub ↔ Regular | (347, 3) | 0.52 | 16% | Usually PRIVATE |
| Regular ↔ Regular | (3, 2) | 0.18 | 2% | Almost always PRIVATE |

### Interaction Between Endpoints

Both endpoints' degrees determine the edge's visibility:

```
                          Endpoint v's Degree
                    Low (1-10)   Medium (10-100)   High (100+)
                  ┌────────────┬─────────────────┬────────────┐
    Low (1-10)    │  PRIVATE   │    PRIVATE      │  PRIVATE   │
                  │   (2%)     │     (8%)        │   (16%)    │
                  ├────────────┼─────────────────┼────────────┤
Endpoint  Medium  │  PRIVATE   │    MIXED        │   MIXED    │
u's       (10-100)│   (8%)     │    (20%)        │   (30%)    │
Degree            ├────────────┼─────────────────┼────────────┤
    High (100+)   │  PRIVATE   │    MIXED        │  PUBLIC    │
                  │   (16%)    │    (30%)        │   (40%)    │
                  └────────────┴─────────────────┴────────────┘
```

---

## TRUE Edge-LDP Algorithms

### Core Mechanism: Randomized Response

Each edge locally perturbs its existence bit:

```python
def privatize(true_bit, epsilon):
    p = exp(epsilon) / (1 + exp(epsilon))  # Probability of truth
    
    if random() < p:
        return true_bit      # Report true value
    else:
        return not true_bit  # Report flipped value
```

**Theorem**: Randomized Response satisfies ε-LDP.

### Algorithm 1: Edge Count

```
LOCAL (at each edge):
    if is_public:
        report = true_value    # No noise
    else:
        report = RR(true_value, ε)   # Randomized Response

AGGREGATE:
    public_count = exact count of public edges
    private_count = debiased estimate from noisy reports
    total = public_count + private_count
```

### Algorithm 2: Two-Round Protocol (for Subgraph Counting)

For triangles, k-stars, and max degree, we use a **Two-Round Protocol**:

```
┌─────────────────────────────────────────────────────────────────┐
│                   TWO-ROUND PROTOCOL                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ROUND 1 (ε/2-LDP per edge):                                   │
│  • Each edge reports existence via RR(ε/2)                     │
│  • Aggregator builds noisy adjacency matrix Â                  │
│                                                                 │
│  ROUND 2 (ε/2-LDP per edge):                                   │
│  • Each edge reports existence AGAIN with fresh randomness     │
│  • Aggregator builds second noisy matrix B̂                     │
│                                                                 │
│  AGGREGATE:                                                     │
│  • Count subgraphs using Â and B̂                               │
│  • Debias to get unbiased estimate                             │
│                                                                 │
│  PRIVACY: ε/2 + ε/2 = ε total (sequential composition)         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Available Algorithms

| Algorithm | Class | Sensitivity |
|-----------|-------|-------------|
| Edge Count | `LDPEdgeCounter` | Δ = 1 |
| Max Degree | `TwoRoundEdgeLDPMaxDegree` | Δ = 1 |
| Triangles | `TwoRoundEdgeLDPTriangleCounter` | Δ = n-2 |
| k-Stars | `TwoRoundEdgeLDPKStarCounter` | Δ = C(n-2, k-1) |

---

## Installation & Usage

### Prerequisites

```bash
pip install networkx numpy scipy
```

### Quick Start

```python
from visibility_aware_edge_ldp.powerlaw_dataset import PowerLawDataset
from visibility_aware_edge_ldp.model import VisibilityPolicy, VisibilityAwareGraph
from visibility_aware_edge_ldp.true_ldp import TrueLDPSystem

# Step 1: Load SNAP Facebook dataset with power-law verification
dataset = PowerLawDataset(
    dataset_name='facebook',        # SNAP Facebook dataset
    target_public_fraction=0.2,     # 20% edges will be PUBLIC
    seed=42,                        # Reproducibility
    verify_powerlaw=True            # Verify P(k) ∝ k^(-α)
)

# Step 2: Get subgraph (optional, for faster testing)
G = dataset.get_subgraph(n_nodes=500)

# Step 3: Create visibility policy (binary model)
policy = VisibilityPolicy(
    public_fraction=0.2,    # Target 20% PUBLIC
    binary_model=True       # Only PUBLIC/PRIVATE (no intermediate)
)

# Step 4: Create visibility-aware graph
va_graph = VisibilityAwareGraph(
    G,
    policy,
    probabilistic=True,     # Degree-based probability assignment
    seed=42
)

# Step 5: Initialize TRUE LDP system
system = TrueLDPSystem(epsilon=2.0)

# Step 6: Run privacy-preserving queries
edge_count, proof = system.estimate_edge_count(va_graph)
max_degree, proof = system.estimate_max_degree(va_graph)
triangles, proof = system.estimate_triangles(va_graph)
stars_3, proof = system.estimate_kstars(va_graph, k=3)

# Step 7: Print results
print(f"Edge count: {edge_count}")
print(f"Max degree: {max_degree}")
print(f"Triangles: {triangles}")
print(f"3-stars: {stars_3}")

# Step 8: Run all queries at once
results = system.run_all(va_graph)
```

### Checking Visibility Classification

```python
# Get visibility statistics
public_edges = va_graph.get_public_edges()
private_edges = va_graph.get_private_edges()
counts = va_graph.get_visibility_counts()

print(f"PUBLIC edges: {len(public_edges)}")
print(f"PRIVATE edges: {len(private_edges)}")
print(f"Public fraction: {len(public_edges) / (len(public_edges) + len(private_edges)):.1%}")

# Check specific edge
from visibility_aware_edge_ldp.model import VisibilityClass
vis = va_graph.get_visibility(0, 1)
if vis == VisibilityClass.PUBLIC:
    print("Edge (0,1) is PUBLIC")
else:
    print("Edge (0,1) is PRIVATE")
```

---

## API Reference

### `PowerLawDataset`

```python
PowerLawDataset(
    dataset_name='facebook',       # 'facebook', 'twitter', 'email', 'synthetic'
    data_dir='./data',             # Directory for data files
    target_public_fraction=0.2,    # Target fraction of public edges
    seed=42,                       # Random seed
    verify_powerlaw=True           # Run power-law verification
)
```

**Methods:**
- `get_subgraph(n_nodes)` - Get subgraph with top n nodes by degree
- `get_public_edges()` - Set of public edges
- `get_private_edges()` - Set of private edges
- `is_public(u, v)` - Check if edge is public
- `print_summary()` - Print dataset statistics

### `VisibilityPolicy`

```python
VisibilityPolicy(
    public_fraction=0.2,           # Fraction of PUBLIC edges
    binary_model=True              # Use only PUBLIC/PRIVATE
)
```

### `VisibilityAwareGraph`

```python
VisibilityAwareGraph(
    G,                             # NetworkX graph
    policy,                        # VisibilityPolicy
    probabilistic=True,            # Degree-based assignment
    seed=42                        # Random seed
)
```

**Methods:**
- `get_visibility(u, v)` - Get VisibilityClass for edge
- `get_public_edges()` - Set of public edges
- `get_private_edges()` - Set of private edges
- `get_visibility_counts()` - Dict of counts per class

### `TrueLDPSystem`

```python
TrueLDPSystem(epsilon=1.0)         # Privacy parameter
```

**Methods:**
- `estimate_edge_count(va_graph)` - Returns (estimate, proof)
- `estimate_max_degree(va_graph)` - Returns (estimate, proof)
- `estimate_triangles(va_graph)` - Returns (estimate, proof)
- `estimate_kstars(va_graph, k)` - Returns (estimate, proof)
- `run_all(va_graph)` - Returns dict with all results

---

## Mathematical Foundations

### Local Differential Privacy (LDP)

**Definition**: Mechanism M satisfies ε-LDP if for all inputs x, x' and outputs S:

$$\Pr[M(x) \in S] \leq e^{\varepsilon} \cdot \Pr[M(x') \in S]$$

### Randomized Response

For binary data b ∈ {0, 1}:

$$p = \frac{e^{\varepsilon}}{1 + e^{\varepsilon}}$$

- With probability p: report true value
- With probability 1-p: report flipped value

**Debiasing**: Given n responses with count ĉ:

$$\hat{n}_{true} = \frac{\hat{c} - n(1-p)}{2p - 1}$$

### Sensitivity Bounds

| Query | Upper Bound Δ | Lower Bound Δ |
|-------|---------------|---------------|
| Edge Count | 1 | 1 |
| Max Degree | 1 | 1 |
| Triangles | n-2 | 1 |
| k-Stars | C(n-2, k-1) | 1 |

### Effective Sensitivity (VA-Edge-LDP Advantage)

$$\Delta_{effective} = \Delta_{base} \times f_{private}$$

With 20% PUBLIC edges: Δ_eff = 0.8 × Δ_base → **20% less noise**

---

## Experimental Results

### Test Configuration

| Parameter | Value |
|-----------|-------|
| Dataset | Facebook SNAP |
| Subgraph | 100-500 nodes |
| ε (epsilon) | 1.0, 2.0, 4.0 |
| Public Fraction | 20% |

### Sample Output

```
Graph: 100 nodes, 2422 edges

True Values:
  Edge count: 2422
  Max degree: 67
  Triangles: 85,710
  3-stars: 4,012,390

Estimates (ε = 2.0):
  Edge count: 2418.3 (error: 0.15%)
  Max degree: 99 (error: 47.8%)
  Triangles: 83,241 (error: 2.9%)
  3-stars: 3,891,002 (error: 3.0%)

Model: ✅ TRUE EDGE-LEVEL LOCAL DP
```

### Privacy-Utility Tradeoff

| ε | Edge Count Error | Triangle Error | Max Degree Error |
|---|------------------|----------------|------------------|
| 1.0 | 2.1% | 8.4% | 65% |
| 2.0 | 0.5% | 2.9% | 48% |
| 4.0 | 0.1% | 0.8% | 25% |

---

## File Structure

```
visibility_aware_edge_ldp/
├── __init__.py
├── model.py                 # Visibility model (PUBLIC/PRIVATE)
├── powerlaw_dataset.py      # SNAP dataset loader & power-law verification
├── true_ldp.py              # TRUE Edge-LDP algorithms
├── evaluate_edge_ldp.py     # Evaluation scripts
├── evaluate_true_ldp.py     # TRUE LDP evaluation
├── compare_ldp.py           # Comparison utilities
├── uniform_ldp.py           # Uniform LDP baseline
├── README.md                # This file
└── VA_EDGE_LDP_COMPLETE_WRITEUP.md  # Full technical documentation

data/
└── facebook_combined.txt    # SNAP Facebook dataset
```

---

## References

1. Warner, S. L. (1965). Randomized response: A survey technique for eliminating evasive answer bias. *JASA*.
2. Dwork, C., & Roth, A. (2014). The algorithmic foundations of differential privacy. *Foundations and Trends in TCS*.
3. Imola, J., Murakami, T., & Chaudhuri, K. (2021). Locally differentially private analysis of graph statistics. *USENIX Security*.
4. McAuley, J., & Leskovec, J. (2012). Learning to discover social circles in ego networks. *NIPS*.
5. Clauset, A., Shalizi, C. R., & Newman, M. E. (2009). Power-law distributions in empirical data. *SIAM Review*.

---

## License

MIT License

---

## Citation

If you use this framework, please cite:

```bibtex
@software{va_edge_ldp,
  title={Visibility-Aware Edge Local Differential Privacy},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/va-edge-ldp}
}
```

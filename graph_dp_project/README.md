# Visibility-Aware Edge Local Differential Privacy (VA-Edge-LDP)

## Overview

This project implements a **visibility-aware edge local differential privacy (VA-Edge-LDP)** framework for privacy-preserving social graph analytics. Unlike traditional approaches that treat all edges uniformly, our method distinguishes between **public edges** (e.g., organizational affiliations) and **private edges** (e.g., personal friendships) to achieve better accuracy while maintaining rigorous privacy guarantees.

**Key Achievement**: At privacy budget ε=2.0, we achieve **0.01% error** for edge count and **16.44% error** for triangle count on a 300-node Facebook network.

## Project Structure

```
DP/
├── visibility_aware_edge_ldp/       # Core library
│   ├── __init__.py                  # Package initialization
│   ├── model_binary.py              # Visibility model and graph classes
│   └── true_ldp.py                  # LDP protocols and algorithms
│
├── data/                            # Datasets
│   ├── facebook_combined.txt        # Full Facebook network (4,039 nodes)
│   ├── facebook_subset.edgelist     # Subset (300 nodes, 13,327 edges)
│   ├── facebook_subset_visibility.json  # Edge visibility labels
│   └── facebook_subset_metadata.json    # Dataset statistics
│
├── results/                         # Experiment outputs
│   ├── fast_experiments.json        # Raw results (generated)
│   ├── all_results.png              # Performance plot (generated)
│   └── results_table.png            # Results table (generated)
│
├── quick_subset.py                  # Extract power-law subset
├── generate_visibility_dataset.py   # Assign visibility labels
├── run_fast_experiments.py          # Main experiment runner
├── plot_results.py                  # Plotting utilities
├── requirements.txt                 # Python dependencies
└── sigplanconf-template (1).tex     # Research paper (POPL'26)
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Steps

1. **Navigate to project directory**:
   ```bash
   cd DP
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**:
   
   **Windows (PowerShell)**:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   
   **Linux/Mac**:
   ```bash
   source .venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

Dependencies installed:
- `numpy` - Numerical computing
- `networkx` - Graph algorithms
- `matplotlib` - Visualization
- `scipy` - Statistical analysis

## Quick Start

Run complete experiments (takes ~5 minutes):

```bash
python run_fast_experiments.py
```

This will:
- Load Facebook network subset (300 nodes, 13,327 edges)
- Test 4 privacy budgets (ε = 0.5, 1.0, 2.0, 4.0)
- Run 5 queries: edge count, max degree, triangles, 2-stars, 3-stars
- Execute 5 trials per configuration
- Generate plots in `results/` directory

**Expected Output**:
```
Loading subset...
  300 nodes, 13,327 edges
  Public: 2,704 (20.3%)

Computing ground truth...
  edge_count: 13,327
  max_degree: 299
  triangles: 305,615
  2_stars: 1,525,988
  3_stars: 67,450,746

Running experiments (4 ε × 5 trials × 5 queries)...
...
Results saved: results/fast_experiments.json
Plots saved: results/all_results.png
```

## File Descriptions

### Core Library Files

#### `visibility_aware_edge_ldp/__init__.py`
Package initialization. Exports main classes:
- `VisibilityClass` - Enum for PUBLIC/PRIVATE edge types
- `VisibilityAwareGraph` - Graph with visibility labels
- `TrueLDPSystem` - Complete LDP protocol implementation
- `RandomizedResponse` - Basic RR mechanism

#### `visibility_aware_edge_ldp/model_binary.py`
**Purpose**: Define the visibility-aware graph model.

**Key Classes**:
- `VisibilityClass(Enum)`: Binary classification (PUBLIC, PRIVATE)
- `VisibilityAwareGraph`: Wraps NetworkX graph with edge visibility labels

**Key Features**:
- Stores edge-to-visibility mapping
- Computes statistics (# public edges, # private edges, fraction)
- Provides query methods: `get_visibility()`, `get_public_edges()`, `get_private_edges()`
- Implements visibility assignment strategies (degree-based, random)

**Example Usage**:
```python
from visibility_aware_edge_ldp import VisibilityAwareGraph, VisibilityClass

# Assign visibility
edge_visibility = {}
for u, v in G.edges():
    edge_visibility[(u, v)] = VisibilityClass.PUBLIC if u < 5 else VisibilityClass.PRIVATE

va_graph = VisibilityAwareGraph(G, edge_visibility)
print(va_graph.summary())
```

#### `visibility_aware_edge_ldp/true_ldp.py`
**Purpose**: Implement all LDP protocols.

**Key Classes**:
- `RandomizedResponse`: Classic RR mechanism with parameter p = e^ε/(1+e^ε)
- `TrueLDPSystem`: Complete two-round protocol for all queries

**Implemented Algorithms**:

1. **Edge Count** (Lines 50-100):
   - Single-round protocol
   - Queries all O(n²) possible edges
   - PUBLIC edges reported exactly, PRIVATE via RR
   - Unbiased estimator: (n₁ - n·q) / (2p-1)

2. **Max Degree** (Lines 200-350):
   - Two-round protocol (ε/2 per round)
   - Round 1: Estimate all degrees, identify top-k candidates
   - Round 2: Refine candidates with debiasing
   - Formula: d̂_priv = (confirmed - n_pot·q₁·q₂) / (p₁·p₂)

3. **Triangle Count** (Lines 400-600):
   - Two-round with IPW weighting
   - Round 1: Build noisy edge set, find candidate triangles
   - Round 2: Confirm candidates
   - IPW weight: w = 1 / (p₁·p₂)^n_priv (capped at 50)
   - False positive correction applied

4. **K-Star Count** (Lines 650-800):
   - Estimates degrees first, then computes Σ C(d(v), k)
   - Uses combined debiasing + IPW
   - Supports k=2 (2-stars) and k=3 (3-stars)

**Privacy Guarantee**: All protocols satisfy **ε-VA-Edge-LDP** (Definition 3.1 in paper):
- Each PRIVATE edge: ε-LDP independently
- PUBLIC edges: No noise (already public)
- Composition: Two rounds use ε/2 each

### Script Files

#### `quick_subset.py`
**Purpose**: Extract a power-law subset from the full Facebook graph.

**What it does**:
1. Loads `facebook_combined.txt` (4,039 nodes)
2. Performs BFS from high-degree nodes to extract 300 nodes
3. Verifies power-law degree distribution (α ≈ 2.5)
4. Assigns visibility labels (~20% public)
5. Saves to `facebook_subset.edgelist` and `facebook_subset_visibility.json`

**Run**: `python quick_subset.py`

**Output**: 
- `data/facebook_subset.edgelist` - Edge list
- `data/facebook_subset_visibility.json` - Visibility labels
- `data/facebook_subset_metadata.json` - Statistics

#### `generate_visibility_dataset.py`
**Purpose**: Assign visibility labels to an existing graph.

**Strategies**:
- Degree-based: High-degree nodes have more public edges
- Random: Uniform random with target fraction (e.g., 20% public)

**Run**: `python generate_visibility_dataset.py`

#### `run_fast_experiments.py`
**Purpose**: Main experiment runner.

**What it does**:
1. Loads Facebook subset with visibility
2. Computes ground truth (edge count, max degree, triangles, k-stars)
3. Tests 4 privacy budgets: ε ∈ {0.5, 1.0, 2.0, 4.0}
4. Runs 5 trials per configuration
5. Computes error metrics (mean, std, relative error)
6. Saves raw results to JSON
7. Generates publication-quality plots

**Run**: `python run_fast_experiments.py`

**Output**:
- `results/fast_experiments.json` - Raw results
- `results/all_results.png` - 5-panel performance plot
- `results/results_table.png` - Summary table

**Runtime**: ~5 minutes on modern CPU

#### `plot_results.py`
**Purpose**: Standalone plotting from existing JSON results.

**Run**: `python plot_results.py`

Uses: If you already have `results/fast_experiments.json` and just want to regenerate plots.

### Data Files

#### `facebook_combined.txt`
- **Source**: Stanford SNAP dataset
- **Size**: 4,039 nodes, 88,234 edges
- **Format**: Space-separated edge list
- **Description**: Full Facebook social network from survey

#### `facebook_subset.edgelist`
- **Size**: 300 nodes, 13,327 edges
- **Properties**: Power-law degree distribution (α ≈ 2.5)
- **Extraction**: BFS from high-degree nodes
- **Format**: Space-separated edge list

#### `facebook_subset_visibility.json`
- **Format**: JSON mapping "u,v" → "PUBLIC" or "PRIVATE"
- **Statistics**: 2,704 public (20.3%), 10,623 private (79.7%)
- **Assignment**: Uniform random with 20% target

#### `facebook_subset_metadata.json`
- **Contents**: Dataset statistics (nodes, edges, visibility counts, degree stats)

## Experimental Results

Results on 300-node Facebook subset at **ε=2.0**:

| Query       | Ground Truth | Estimate   | Std Dev | Relative Error |
|-------------|--------------|------------|---------|----------------|
| Edge Count  | 13,327       | 13,326     | 39      | **0.01%**      |
| Max Degree  | 299          | 291        | 7       | 2.52%          |
| Triangles   | 305,615      | 355,865    | 7,999   | **16.44%**     |
| 2-Stars     | 1,525,988    | 1,221,784  | 30,001  | 19.93%         |
| 3-Stars     | 67,450,746   | 48,415,579 | 1,786K  | 28.22%         |

**Key Observations**:
- Simple queries (edge count, max degree) achieve sub-3% error
- Complex queries (triangles, k-stars) maintain practical accuracy
- Error decreases exponentially with privacy budget
- 20% public edges provide significant variance reduction vs uniform LDP

## Algorithm Details

### Two-Round Protocol Structure

All complex queries follow this pattern:

**Round 1** (budget ε/2):
- Query all possible edges via RR with p₁ = e^(ε/2)/(1+e^(ε/2))
- PUBLIC edges reported exactly
- PRIVATE edges via randomized response
- Build noisy candidate set

**Round 2** (budget ε/2):
- Confirm candidates with fresh RR (p₂ = e^(ε/2)/(1+e^(ε/2)))
- Apply debiasing: remove expected false positives
- Apply IPW: reweight by detection probability
- Aggregate final estimate

**Privacy Cost**: ε/2 + ε/2 = ε (sequential composition)

### Inverse Probability Weighting (IPW)

For triangles/k-stars with n_priv private edges:
- Detection probability: p_detect = (p₁·p₂)^n_priv
- IPW weight: w = 1 / p_detect
- Capped at 50 to prevent variance explosion
- Variance penalty applied if p_detect < 0.3

**Why IPW?** Corrects selection bias from non-uniform detection rates across different edge visibility patterns.

## Privacy Guarantees

### Formal Definition (ε-VA-Edge-LDP)

For graph G with visibility function ν:
1. Each **PRIVATE** edge e satisfies ε-LDP:
   ```
   Pr[M(G) ∈ S] ≤ e^ε · Pr[M(G') ∈ S]
   ```
   for neighboring graphs G, G' differing only in e.

2. **PUBLIC** edges reported exactly (no noise).

### What This Means

- **Untrusted Aggregator**: No need to trust central server
- **Per-Edge Protection**: Each private relationship protected independently
- **Post-Processing**: IPW and debiasing preserve privacy (deterministic operations)
- **Composition**: Multiple rounds compose sequentially

### Threat Model

**Adversary knows**:
- All PUBLIC edges
- Visibility labels (which edges are public/private)
- Noisy reports from all edge positions

**Adversary cannot**:
- Determine with confidence >e^ε whether specific PRIVATE edge exists
- Infer private edges even with background knowledge

## Usage Examples

### Basic Usage

```python
import networkx as nx
from visibility_aware_edge_ldp import VisibilityAwareGraph, VisibilityClass, TrueLDPSystem

# Load graph
G = nx.karate_club_graph()

# Assign visibility (20% public)
edge_visibility = {}
for i, (u, v) in enumerate(G.edges()):
    if i < len(G.edges()) // 5:
        edge_visibility[(u, v)] = VisibilityClass.PUBLIC
    else:
        edge_visibility[(u, v)] = VisibilityClass.PRIVATE

# Create VA graph
va_graph = VisibilityAwareGraph(G, edge_visibility)

# Run LDP queries
ldp = TrueLDPSystem(va_graph, epsilon=2.0)

edge_count = ldp.estimate_edge_count(trials=5)
max_degree = ldp.estimate_max_degree(trials=5)
triangles = ldp.estimate_triangle_count(trials=5)

print(f"Edge count: {edge_count} (true: {G.number_of_edges()})")
print(f"Max degree: {max_degree} (true: {max(dict(G.degree()).values())})")
print(f"Triangles: {triangles} (true: {sum(nx.triangles(G).values()) // 3})")
```

### Load Existing Dataset

```python
import networkx as nx
import json
from visibility_aware_edge_ldp import VisibilityAwareGraph, VisibilityClass

# Load graph
G = nx.read_edgelist("data/facebook_subset.edgelist", nodetype=int)

# Load visibility
with open("data/facebook_subset_visibility.json", 'r') as f:
    vis_data = json.load(f)

edge_visibility = {}
for edge_str, vis_str in vis_data.items():
    u, v = map(int, edge_str.split(','))
    edge_visibility[(u, v)] = VisibilityClass(vis_str)

va_graph = VisibilityAwareGraph(G, edge_visibility)
```

## License

MIT License. See dataset sources for their respective licenses.

## Contact

For questions or issues, please open an issue or contact the authors.

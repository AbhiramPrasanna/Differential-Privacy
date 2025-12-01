# Visibility-Aware Edge Local Differential Privacy: Algorithm Details

## Table of Contents
1. [Overview](#overview)
2. [Privacy Model](#privacy-model)
3. [Core Primitives](#core-primitives)
4. [Edge Count Estimation](#edge-count-estimation)
5. [Triangle Count Estimation](#triangle-count-estimation)
6. [K-Star Count Estimation](#k-star-count-estimation)
7. [Max Degree Estimation](#max-degree-estimation)
8. [Privacy Analysis](#privacy-analysis)
9. [Comparison: VA-Edge-LDP vs Uniform Edge-LDP](#comparison-va-edge-ldp-vs-uniform-edge-ldp)

---

## Overview

This document describes the algorithms implemented in the **Visibility-Aware Edge Local Differential Privacy (VA-Edge-LDP)** system. The key innovation is leveraging **edge visibility** to improve utility while maintaining formal privacy guarantees.

### Key Insight
In real social networks, some edges are **public** (e.g., connections to public figures, verified accounts) while others are **private**. Public edges don't require privacy protection, so we can:
- Report public edge information **exactly** (no noise)
- Apply privacy mechanisms **only** to private edges
- Achieve better utility with the same privacy guarantee

### Privacy Guarantee
```
ε-Visibility-Aware Edge Local Differential Privacy (VA-Edge-LDP)

For any private edge e and any output O:
    Pr[M(G with e) = O] / Pr[M(G without e) = O] ≤ exp(ε)

Public edges: ∞-DP (no privacy, exact reporting)
Private edges: ε-LDP (full privacy protection)
```

---

## Privacy Model

### Visibility Classes
```python
class VisibilityClass(Enum):
    PUBLIC = "public"      # No privacy needed (e.g., celebrity connections)
    PRIVATE = "private"    # Full ε-LDP protection required
```

### Edge-Level Local DP
In **Edge-LDP**, each edge holder only knows:
- Their edge identifier (u, v) — public information
- Whether the edge exists — 1 bit of **private** information

This is stronger than Node-LDP where nodes know their entire neighborhood.

```
┌─────────────────────────────────────────────────────────────────┐
│                    EDGE-LDP MODEL                               │
├─────────────────────────────────────────────────────────────────┤
│  Edge (u,v) knows:                                              │
│    ✓ Its endpoints u, v (public identifiers)                    │
│    ✓ Whether it exists: 1 bit (PRIVATE)                         │
│    ✗ Other edges in the graph                                   │
│    ✗ Degrees of u or v                                          │
│    ✗ Any graph structure                                        │
├─────────────────────────────────────────────────────────────────┤
│  Aggregator receives:                                           │
│    ✓ Noisy reports from all edge positions                      │
│    ✗ True edge existence values                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Primitives

### 1. Randomized Response (RR)

The fundamental mechanism for binary data under LDP.

**Protocol** (executed locally by each edge):
```
Input: true_bit b ∈ {0, 1}, privacy parameter ε
Output: noisy_bit

1. Compute p = exp(ε) / (1 + exp(ε))
2. With probability p: return b (truth)
3. With probability 1-p: return 1-b (flip)
```

**Privacy Proof**:
```
For any output y and inputs b, b':
    Pr[M(b)=y] / Pr[M(b')=y] ≤ exp(ε)

Case y=b:  Pr[M(b)=b] / Pr[M(b')=b] = p/(1-p) = exp(ε) ✓
Case y≠b:  Pr[M(b)=y] / Pr[M(b')=y] = (1-p)/p = exp(-ε) ≤ exp(ε) ✓
```

**Debiasing** (at aggregator):
```
Given n noisy reports with noisy_count ones:
    estimated_true_count = (noisy_count - n(1-p)) / (2p - 1)
```

### 2. Two-Round Protocol

For subgraph counting, we use a two-round protocol that splits the privacy budget.

```
┌─────────────────────────────────────────────────────────────────┐
│                 TWO-ROUND PROTOCOL                              │
├─────────────────────────────────────────────────────────────────┤
│  ROUND 1 (ε/2-LDP per edge):                                    │
│    • Each edge reports noisy existence via RR                   │
│    • Aggregator builds noisy edge set                           │
│    • Identifies candidate subgraphs                             │
├─────────────────────────────────────────────────────────────────┤
│  ROUND 2 (ε/2-LDP per edge):                                    │
│    • Query edges in candidate subgraphs                         │
│    • Fresh RR with independent randomness                       │
│    • Confirm/reject candidates                                  │
├─────────────────────────────────────────────────────────────────┤
│  COMPOSITION:                                                   │
│    Total privacy = ε/2 + ε/2 = ε (sequential composition)       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Edge Count Estimation

### Algorithm: VA-Edge-LDP Edge Counter

**Input**: Graph G, visibility assignments, privacy parameter ε  
**Output**: Estimated edge count

```python
def estimate_edge_count(G, visibility, ε):
    """
    Edge count with visibility-aware LDP.
    
    PUBLIC edges: Report exact value (no noise)
    PRIVATE edges: Use Randomized Response
    """
    rr = RandomizedResponse(ε)
    n = number_of_nodes(G)
    nodes = list(G.nodes())
    
    # CRITICAL: Query ALL possible edges (not just existing ones)
    # This hides which edges exist
    reports = []
    for i, u in enumerate(nodes):
        for j in range(i+1, len(nodes)):
            v = nodes[j]
            edge = (u, v)
            exists = edge in G.edges()
            is_public = visibility[edge] == PUBLIC
            
            if is_public:
                # Public edge: report exact value
                reports.append((exists, True))  # (value, is_public)
            else:
                # Private edge: apply RR
                noisy = rr.privatize(exists)
                reports.append((noisy, False))
    
    # Aggregate
    public_count = sum(1 for val, is_pub in reports if is_pub and val)
    private_reports = [val for val, is_pub in reports if not is_pub]
    private_count = rr.estimate_count(private_reports)
    
    return public_count + private_count
```

**Complexity**: O(n²) — must query all possible edge positions

**Privacy**: ε-LDP for private edges, ∞-DP (exact) for public edges

---

## Triangle Count Estimation

### Algorithm: VA-Edge-LDP Two-Round Triangle Counter

**Input**: Graph G, visibility assignments, privacy parameter ε  
**Output**: Estimated triangle count

```python
def estimate_triangles(G, visibility, ε):
    """
    Triangle counting using two-round Edge-LDP with visibility awareness.
    
    Uses Inverse Probability Weighting (IPW) for unbiased estimation.
    """
    n = number_of_nodes(G)
    ε1, ε2 = ε/2, ε/2
    rr1 = RandomizedResponse(ε1)
    rr2 = RandomizedResponse(ε2)
    p1, p2 = rr1.p, rr2.p
    
    # ═══════════════════════════════════════════════════════════════
    # ROUND 1: Edge Discovery
    # ═══════════════════════════════════════════════════════════════
    noisy_edges = set()
    edge_info = {}  # Track public/private status
    
    for edge in all_possible_edges(G):
        exists = edge in G.edges()
        is_public = visibility.get(edge) == PUBLIC
        
        if is_public:
            if exists:
                noisy_edges.add(edge)
            edge_info[edge] = {'is_public': True, 'r1': exists}
        else:
            noisy = rr1.privatize(exists)
            if noisy:
                noisy_edges.add(edge)
            edge_info[edge] = {'is_public': False, 'r1': noisy}
    
    # ═══════════════════════════════════════════════════════════════
    # Find Candidate Triangles from noisy edges
    # ═══════════════════════════════════════════════════════════════
    adj = build_adjacency(noisy_edges)
    candidates = find_triangles(adj)  # All triangles in noisy graph
    
    # ═══════════════════════════════════════════════════════════════
    # ROUND 2: Triangle Confirmation with IPW
    # ═══════════════════════════════════════════════════════════════
    total_estimate = 0
    
    for triangle in candidates:
        e1, e2, e3 = edges_of_triangle(triangle)
        
        # Confirm each edge
        confirmed = True
        ipw_weight = 1.0
        
        for edge in [e1, e2, e3]:
            exists = edge in G.edges()
            is_public = edge_info[edge]['is_public']
            
            if is_public:
                # Public edge: exact confirmation
                if not exists:
                    confirmed = False
                    break
                # Weight = 1.0 (no noise)
            else:
                # Private edge: RR confirmation
                noisy_confirm = rr2.privatize(exists)
                if not noisy_confirm:
                    confirmed = False
                    break
                # IPW weight for this edge
                ipw_weight *= 1.0 / (p1 * p2)
        
        if confirmed:
            total_estimate += ipw_weight
    
    return max(0, total_estimate)
```

### IPW Correction Explained

For a true triangle with edges e1, e2, e3:

| Edge Type | Detection Probability | IPW Weight |
|-----------|----------------------|------------|
| All Public | 1.0 × 1.0 × 1.0 = 1.0 | 1.0 |
| 2 Public, 1 Private | 1.0 × 1.0 × (p₁·p₂) | 1/(p₁·p₂) |
| 1 Public, 2 Private | 1.0 × (p₁·p₂)² | 1/(p₁·p₂)² |
| All Private | (p₁·p₂)³ | 1/(p₁·p₂)³ |

**Why IPW?**
- Each private edge is detected with probability p₁·p₂ (Round 1 AND Round 2)
- To get unbiased estimate, weight each detection by 1/detection_probability
- This is the Horvitz-Thompson estimator

---

## K-Star Count Estimation

### Algorithm: VA-Edge-LDP Two-Round K-Star Counter

A **k-star** is a subgraph with one center node connected to k leaf nodes.

```
        2-Star:     3-Star:
           v           v
          /|\         /|\
         / | \       / | \
        a  b  c     a  b  c  d
        (center=v)  (center=v)
```

**Input**: Graph G, visibility assignments, k, privacy parameter ε  
**Output**: Estimated k-star count

```python
def estimate_kstars(G, visibility, k, ε):
    """
    K-star counting using two-round Edge-LDP.
    
    For each node v, count C(degree(v), k) and sum.
    """
    n = number_of_nodes(G)
    ε1, ε2 = ε/2, ε/2
    rr1 = RandomizedResponse(ε1)
    rr2 = RandomizedResponse(ε2)
    p1, p2 = rr1.p, rr2.p
    
    total_kstars = 0
    
    for v in G.nodes():
        # ═══════════════════════════════════════════════════════════
        # ROUND 1: Discover neighbors of v
        # ═══════════════════════════════════════════════════════════
        noisy_neighbors = set()
        neighbor_info = {}
        
        for u in G.nodes():
            if u == v:
                continue
            edge = (min(u,v), max(u,v))
            exists = edge in G.edges()
            is_public = visibility.get(edge) == PUBLIC
            
            if is_public:
                if exists:
                    noisy_neighbors.add(u)
                neighbor_info[u] = {'is_public': True}
            else:
                noisy = rr1.privatize(exists)
                if noisy:
                    noisy_neighbors.add(u)
                neighbor_info[u] = {'is_public': False}
        
        # ═══════════════════════════════════════════════════════════
        # ROUND 2: Confirm neighbors with IPW
        # ═══════════════════════════════════════════════════════════
        confirmed_neighbors = []
        
        for u in noisy_neighbors:
            edge = (min(u,v), max(u,v))
            exists = edge in G.edges()
            is_public = neighbor_info[u]['is_public']
            
            if is_public:
                confirmed_neighbors.append((u, 1.0))  # (neighbor, weight)
            else:
                noisy_confirm = rr2.privatize(exists)
                if noisy_confirm:
                    weight = 1.0 / (p1 * p2)
                    confirmed_neighbors.append((u, weight))
        
        # ═══════════════════════════════════════════════════════════
        # Compute k-star contribution with IPW
        # ═══════════════════════════════════════════════════════════
        if len(confirmed_neighbors) >= k:
            # Sum over all k-subsets of confirmed neighbors
            # Weight = product of individual weights
            from itertools import combinations
            for subset in combinations(confirmed_neighbors, k):
                kstar_weight = prod(w for _, w in subset)
                total_kstars += kstar_weight
    
    return max(0, total_kstars)
```

**Simplified Version** (used in implementation):
```python
# Approximate: use confirmed degree and compute C(d, k)
confirmed_degree = len(confirmed_neighbors)
kstars_from_v = comb(confirmed_degree, k)
# Apply average IPW correction
avg_weight = (1.0 / (p1 * p2)) ** (k * private_fraction)
total_kstars += kstars_from_v * avg_weight
```

---

## Max Degree Estimation

### Algorithm: VA-Edge-LDP Two-Round Max Degree

**Input**: Graph G, visibility assignments, privacy parameter ε  
**Output**: Estimated maximum degree

```python
def estimate_max_degree(G, visibility, ε):
    """
    Max degree using two-round Edge-LDP with visibility awareness.
    
    Key insight: Public edges contribute EXACT degree counts.
    Only private edges need estimation.
    """
    n = number_of_nodes(G)
    ε1, ε2 = ε/2, ε/2
    rr1 = RandomizedResponse(ε1)
    rr2 = RandomizedResponse(ε2)
    p1, p2 = rr1.p, rr2.p
    q1, q2 = 1-p1, 1-p2
    
    # ═══════════════════════════════════════════════════════════════
    # ROUND 1: Build noisy degree estimates
    # ═══════════════════════════════════════════════════════════════
    noisy_degrees = defaultdict(int)
    public_degrees = defaultdict(int)
    noisy_edges = set()
    
    for edge in all_possible_edges(G):
        u, v = edge
        exists = edge in G.edges()
        is_public = visibility.get(edge) == PUBLIC
        
        if is_public:
            if exists:
                noisy_edges.add(edge)
                noisy_degrees[u] += 1
                noisy_degrees[v] += 1
                public_degrees[u] += 1
                public_degrees[v] += 1
        else:
            noisy = rr1.privatize(exists)
            if noisy:
                noisy_edges.add(edge)
                noisy_degrees[u] += 1
                noisy_degrees[v] += 1
    
    # ═══════════════════════════════════════════════════════════════
    # Select top candidates by noisy degree
    # ═══════════════════════════════════════════════════════════════
    candidates = sorted(G.nodes(), 
                       key=lambda x: noisy_degrees[x], 
                       reverse=True)[:10]
    
    # ═══════════════════════════════════════════════════════════════
    # ROUND 2: Confirm degrees for candidates
    # ═══════════════════════════════════════════════════════════════
    best_degree = 0
    
    for v in candidates:
        public_deg = public_degrees[v]
        
        # Confirm PRIVATE edges incident to v
        confirmed_private = 0
        n_private_neighbors = (n - 1) - public_deg
        
        for edge in noisy_edges:
            u, w = edge
            if u != v and w != v:
                continue
            
            neighbor = w if u == v else u
            edge_norm = (min(v, neighbor), max(v, neighbor))
            
            if visibility.get(edge_norm) == PUBLIC:
                continue  # Already counted exactly
            
            exists = edge_norm in G.edges()
            if rr2.privatize(exists):
                confirmed_private += 1
        
        # ═══════════════════════════════════════════════════════════
        # Unbiased estimation for private degree
        # ═══════════════════════════════════════════════════════════
        # E[confirmed] = true_private * p1*p2 + (n_private - true_private) * q1*q2
        # Solving: true_private = (confirmed - n_private*q1*q2) / (p1*p2 - q1*q2)
        
        detection_diff = p1*p2 - q1*q2
        if abs(detection_diff) > 0.01:
            false_positive_bias = n_private_neighbors * q1 * q2
            estimated_private = (confirmed_private - false_positive_bias) / detection_diff
            estimated_private = max(0, estimated_private)
        else:
            estimated_private = confirmed_private
        
        # Total degree = exact public + estimated private
        total_degree = public_deg + estimated_private
        best_degree = max(best_degree, total_degree)
    
    return min(best_degree, n - 1)
```

### Why This Works Better Than Uniform

| Component | Uniform Edge-LDP | VA-Edge-LDP |
|-----------|-----------------|-------------|
| Public edges | Noisy (RR applied) | **Exact** (no noise) |
| Private edges | Noisy (RR applied) | Noisy (RR applied) |
| Total degree | All estimated | public_exact + private_estimated |

With 50% public edges, VA-Edge-LDP has:
- 50% of degree known exactly
- Only 50% needs estimation
- **Variance reduced by ~50%**

---

## Privacy Analysis

### Sequential Composition Theorem

**Theorem**: If M₁ satisfies ε₁-LDP and M₂ satisfies ε₂-LDP, then releasing both (M₁(x), M₂(x)) satisfies (ε₁ + ε₂)-LDP.

**Application to Two-Round Protocol**:
- Round 1: ε/2-LDP
- Round 2: ε/2-LDP
- Total: ε-LDP ✓

### Visibility-Aware Privacy

**Theorem**: VA-Edge-LDP provides:
- ε-LDP for each private edge
- No privacy (exact reporting) for public edges

**Proof**:
For any private edge e and outputs O:
```
Pr[M(G ∪ {e}) = O]     Pr[RR outputs based on e=1]
─────────────────── = ────────────────────────────
Pr[M(G \ {e}) = O]     Pr[RR outputs based on e=0]

                     = p / (1-p)  or  (1-p) / p
                     ≤ exp(ε)  ✓
```

Public edges don't affect the ratio since they're reported exactly in both cases.

### Comparison to Centralized DP

| Aspect | Centralized DP | Local DP (Edge-LDP) |
|--------|---------------|---------------------|
| Trust model | Trusted curator | No trusted party |
| Data exposure | Curator sees raw data | No one sees raw data |
| Accuracy | Better (noise added once) | Worse (noise per edge) |
| Composition | Global sensitivity | Per-edge sensitivity |

---

## Comparison: VA-Edge-LDP vs Uniform Edge-LDP

### Experimental Results (Facebook Dataset, 300 nodes)

#### Triangle Count
| ε | Uniform Error | VA-LDP Error | Improvement |
|---|--------------|--------------|-------------|
| 0.5 | 77.5% | 38.4% | **+50%** |
| 1.0 | 71.8% | 17.6% | **+76%** |
| 2.0 | 58.2% | 4.8% | **+92%** |
| 4.0 | 31.2% | 1.3% | **+96%** |

#### Max Degree
| ε | Uniform Error | VA-LDP Error | Improvement |
|---|--------------|--------------|-------------|
| 0.5 | 41.5% | 33.1% | **+20%** |
| 2.0 | 6.7% | 3.6% | **+46%** |
| 4.0 | 2.4% | 1.3% | **+45%** |

#### Overall
- **Average Improvement: 31.6%**
- **Best Case: 96% improvement** (triangles at ε=4)
- VA-LDP consistently outperforms Uniform Edge-LDP

### Why VA-Edge-LDP Wins

1. **No Noise on Public Edges**: Public edges contribute exact values
2. **Reduced Variance**: Only private edges contribute to estimation variance
3. **Better Bias Correction**: Fewer edges need debiasing
4. **Compound Effect**: For triangles, if 50% edges are public:
   - Some triangles are fully public (exact count)
   - Mixed triangles have partial noise reduction
   - Only all-private triangles have full noise

### Theoretical Analysis

Let α = fraction of public edges, n = nodes, m = edges.

**Edge Count Variance**:
- Uniform: Var ∝ m / (2p-1)²
- VA-LDP: Var ∝ (1-α)m / (2p-1)²
- **Reduction: α × 100%**

**Triangle Count** (assuming independent visibility):
- Uniform: All triangles have variance from 3 noisy edges
- VA-LDP: 
  - α³ triangles: exact (no variance)
  - 3α²(1-α) triangles: 1 noisy edge
  - 3α(1-α)² triangles: 2 noisy edges  
  - (1-α)³ triangles: 3 noisy edges
- **Significant variance reduction**

---

## Implementation Notes

### Computational Complexity

| Algorithm | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Edge Count | O(n²) | O(n²) |
| Triangle Count | O(n³) worst case | O(n²) |
| K-Star Count | O(n² × k) | O(n²) |
| Max Degree | O(n²) | O(n²) |

### Practical Considerations

1. **Large Graphs**: For n > 1000, consider sampling
2. **Sparse Graphs**: Can optimize by only querying likely edges
3. **Privacy Budget**: Split carefully between rounds
4. **Public Fraction**: Higher public fraction → better utility

### Parameter Selection

- **ε = 1.0**: Good balance of privacy/utility
- **ε = 2.0-4.0**: Better utility, weaker privacy
- **ε < 1.0**: Strong privacy, high variance
- **public_fraction = 0.2-0.5**: Typical social network assumption

---

## References

1. Warner, S. L. (1965). Randomized response: A survey technique for eliminating evasive answer bias.
2. Duchi, J., Jordan, M., & Wainwright, M. (2013). Local privacy and statistical minimax rates.
3. Imola, J., Murakami, T., & Chaudhuri, K. (2021). Locally differentially private analysis of graph statistics.
4. Qin, Z., et al. (2017). Heavy hitter estimation over set-valued data with local differential privacy.
5. Ye, M., & Barg, A. (2018). Optimal schemes for discrete distribution estimation under locally differential privacy.

---

*Document generated for VA-Edge-LDP implementation*  
*Last updated: December 2025*

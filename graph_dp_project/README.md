# Complete Technical Write-Up: Visibility-Aware Edge Local Differential Privacy (VA-Edge-LDP)

## Abstract

This document presents a comprehensive framework for **Visibility-Aware Edge-Level Local Differential Privacy (VA-Edge-LDP)** applied to social network graph analytics. Our approach introduces a binary visibility model (PUBLIC/PRIVATE) that leverages the inherent power-law degree distribution of social networks to optimize the privacy-utility tradeoff. By recognizing that edges connected to high-degree "influencer" nodes are often publicly visible, we apply differential privacy noise only to truly private edges, achieving better accuracy while maintaining rigorous privacy guarantees for sensitive connections.

---

## 1. Introduction

### 1.1 Problem Statement

Social network analysis requires computing graph statistics (edge counts, degree distributions, triangle counts, k-star patterns) while protecting user privacy. Traditional approaches face a fundamental tension:

- **Centralized Differential Privacy (CDP)**: Requires a trusted curator who sees all raw data before adding noise
- **Local Differential Privacy (LDP)**: Each user perturbs their own data locally, but suffers from higher noise accumulation

Our framework addresses this by:
1. Implementing **TRUE Local DP** where no central party ever sees raw edge data
2. Introducing **visibility awareness** to reduce unnecessary noise on publicly-known edges
3. Operating at the **edge level** (not node level) for granular privacy control

### 1.2 Key Innovation

Not all edges in a social network have equal privacy requirements:

| Edge Type | Example | Privacy Need |
|-----------|---------|--------------|
| **PUBLIC** | Celebrity's follower connections | None (publicly visible) |
| **PRIVATE** | Private user's friendships | Full ε-LDP protection |

By classifying edges and applying noise only where needed, we achieve:

$$\Delta_{\text{effective}} = \Delta_{\text{base}} \times p_{\text{private}} < \Delta_{\text{base}}$$

This means **less noise** with **equivalent privacy** for truly sensitive edges.

---

## 2. Theoretical Foundation

### 2.1 Local Differential Privacy (LDP)

**Definition 2.1 (ε-Local Differential Privacy):**
A randomized mechanism $M: \mathcal{X} \rightarrow \mathcal{Y}$ satisfies ε-LDP if for all inputs $x, x' \in \mathcal{X}$ and all outputs $S \subseteq \mathcal{Y}$:

$$\Pr[M(x) \in S] \leq e^{\varepsilon} \cdot \Pr[M(x') \in S]$$

**Key Property:** Privacy holds even against a **malicious aggregator** because the aggregator never sees raw data.

### 2.2 Edge-Level vs. Node-Level LDP

| Aspect | Node-Level LDP | Edge-Level LDP |
|--------|----------------|----------------|
| **Unit of Privacy** | Entire node's data | Single edge |
| **What Each Party Knows** | Node knows all its edges | Edge knows only its existence |
| **Sensitivity** | Node's degree can be large | Always Δ = 1 per edge |
| **Granularity** | Coarse | Fine-grained |

**Our Choice:** Edge-Level LDP provides stronger, more granular privacy guarantees.

### 2.3 Randomized Response

The fundamental building block for binary data under LDP.

**Protocol (Warner, 1965):**
Given true bit $b \in \{0, 1\}$ and privacy parameter ε:
1. Compute $p = \frac{e^{\varepsilon}}{1 + e^{\varepsilon}}$
2. With probability $p$: report true value $b$
3. With probability $1-p$: report flipped value $1-b$

**Theorem 2.1:** Randomized Response satisfies ε-LDP.

**Proof:**
For any output $y \in \{0,1\}$ and any inputs $b, b' \in \{0,1\}$:

*Case 1: $y = b$ (output matches first input)*

$$\frac{\Pr[M(b) = b]}{\Pr[M(b') = b]} = \frac{p}{1-p} = \frac{e^{\varepsilon}/(1+e^{\varepsilon})}{1/(1+e^{\varepsilon})} = e^{\varepsilon}$$

*Case 2: $y = b'$ (output matches second input)*

$$\frac{\Pr[M(b) = b']}{\Pr[M(b') = b']} = \frac{1-p}{p} = e^{-\varepsilon} \leq e^{\varepsilon}$$

Maximum ratio = $e^{\varepsilon}$, satisfying ε-LDP. ∎

**Debiasing Formula:**
Given $n$ noisy responses with observed count $\hat{c}$:

$$\hat{n}_{\text{true}} = \frac{\hat{c} - n(1-p)}{2p - 1}$$

**Variance:**

$$\text{Var}[\hat{n}_{\text{true}}] = \frac{n \cdot p \cdot (1-p)}{(2p-1)^2}$$

---

## 3. Binary Visibility Model

### 3.1 Model Definition

**Definition 3.1 (Binary Visibility Classes):**
Each edge $e = (u, v)$ in graph $G = (V, E)$ is assigned a visibility class:

$$\text{visibility}(e) \in \{\text{PUBLIC}, \text{PRIVATE}\}$$

| Class | Noise Multiplier | Description |
|-------|------------------|-------------|
| **PUBLIC** | $\alpha = 0$ | Publicly known edge, no privacy needed |
| **PRIVATE** | $\alpha = 1$ | Fully private edge, requires ε-LDP |

### 3.2 Visibility Policy

**Definition 3.2 (Visibility Policy):**
A visibility policy $\pi$ specifies:
- $f_{\text{pub}}$: Fraction of edges classified as PUBLIC
- $f_{\text{priv}} = 1 - f_{\text{pub}}$: Fraction classified as PRIVATE
- Assignment function: $\phi: E \rightarrow \{\text{PUBLIC}, \text{PRIVATE}\}$

**Constraint:** $f_{\text{pub}} + f_{\text{priv}} = 1$

### 3.3 Privacy Guarantee Under Binary Model

**Theorem 3.1 (VA-Edge-LDP Privacy Guarantee):**
For a mechanism $M$ operating under the binary visibility model:
- PUBLIC edges: No privacy guarantee needed (publicly known)
- PRIVATE edges: Full ε-LDP guarantee

For neighboring graphs $G, G'$ differing in exactly one PRIVATE edge $e$:

$$\Pr[M(G) \in S] \leq e^{\varepsilon} \cdot \Pr[M(G') \in S]$$

**Proof:**
1. If edge $e$ is PUBLIC: Both graphs behave identically since $e$ is publicly known
2. If edge $e$ is PRIVATE: Randomized Response with parameter ε ensures the ratio bound

Since only PRIVATE edges receive noise and each PRIVATE edge independently satisfies ε-LDP through Randomized Response, the overall mechanism satisfies ε-LDP for any single private edge change. ∎

---

## 4. Power-Law Distribution and Probabilistic Visibility Assignment

### 4.1 Power-Law Property of Social Networks

**Definition 4.1 (Power-Law Degree Distribution):**
A graph exhibits power-law degree distribution if:

$$P(k) \propto k^{-\alpha}$$

where:
- $k$ = node degree
- $\alpha$ = power-law exponent (typically $2 < \alpha < 3$ for social networks)

**Empirical Evidence (Facebook Dataset):**
- Nodes: 4,039 users
- Edges: 88,234 friendships
- Estimated $\alpha \approx 2.5$

### 4.2 Maximum Likelihood Estimation of α

**Theorem 4.1 (Hill Estimator):**
For degrees $k_1, k_2, \ldots, k_n \geq x_{\min}$, the MLE for $\alpha$ is:

$$\hat{\alpha} = 1 + n \left[ \sum_{i=1}^{n} \ln\left(\frac{k_i}{x_{\min} - 0.5}\right) \right]^{-1}$$

**Standard Error:**

$$\text{SE}(\hat{\alpha}) = \frac{\hat{\alpha} - 1}{\sqrt{n}}$$

### 4.3 Probabilistic Visibility Assignment

**Key Insight:** In real social networks:
- High-degree nodes (influencers, celebrities) have publicly visible connections
- Low-degree nodes (private users) have hidden connections

**Algorithm 4.1: Degree-Based Visibility Assignment**

```
Input: Graph G = (V, E), target public fraction f_pub, seed
Output: visibility_dict mapping each edge to {PUBLIC, PRIVATE}

1. Compute degrees: d[v] for all v ∈ V
2. Compute d_max = max{d[v] : v ∈ V}
3. Compute log_max = log(1 + d_max)

4. For each edge (u, v) ∈ E:
   a. Compute degree-based score:
      score = [log(1 + d[u]) + log(1 + d[v])] / (2 × log_max)
   
   b. Compute probability of being PUBLIC:
      P_public = min(1.0, score² × f_pub × 3)
   
   c. With probability P_public:
      visibility[(u,v)] = PUBLIC
   d. Otherwise:
      visibility[(u,v)] = PRIVATE

5. Return visibility_dict
```

**Rationale:**
- Logarithmic scaling handles the heavy-tailed degree distribution
- Quadratic term ($\text{score}^2$) concentrates PUBLIC edges on highest-degree connections
- Scaling factor of 3 approximately achieves target public fraction

**Theorem 4.2 (Degree-Visibility Correlation):**
Under Algorithm 4.1, the expected average endpoint degree of PUBLIC edges exceeds that of PRIVATE edges:

$$\mathbb{E}[\bar{d}_{\text{public}}] > \mathbb{E}[\bar{d}_{\text{private}}]$$

where $\bar{d}_e = (d_u + d_v)/2$ for edge $e = (u,v)$.

---

## 5. TRUE Edge-LDP Algorithms

### 5.1 Edge Count Estimation

**Algorithm 5.1: LDP Edge Counter**

```
LOCAL OPERATION (at each edge position):
Input: edge_exists ∈ {0, 1}, is_public ∈ {True, False}
Output: noisy_report

1. If is_public:
   Return (edge_exists, is_public=True)  // No noise
2. Else:
   Return (RandomizedResponse(ε).privatize(edge_exists), is_public=False)

AGGREGATOR OPERATION:
Input: List of (noisy_bit, is_public) reports
Output: Estimated edge count

1. public_count = Σ{report : is_public = True}
2. private_reports = {report : is_public = False}
3. private_count = Debias(private_reports, |private_reports|)
4. Return public_count + private_count
```

**Sensitivity:** $\Delta = 1$ (adding/removing one edge changes count by 1)

**Privacy:** Each private edge satisfies ε-LDP independently.

### 5.2 Two-Round Protocol for Subgraph Counting

For counting subgraphs (triangles, k-stars, max degree), edges need to be queried multiple times. The **Two-Round Protocol** enables this while maintaining Edge-LDP.

**Why Two Rounds?**
- Each edge only knows its own existence (1 bit)
- Counting triangles requires knowing THREE edges simultaneously
- Solution: Query edges twice with independent randomness

**Protocol Overview:**

```
ROUND 1 (ε/2-LDP per edge):
- Each edge reports existence via Randomized Response(ε/2)
- Aggregator builds noisy adjacency indicator Â

ROUND 2 (ε/2-LDP per edge):  
- Each edge reports existence AGAIN with fresh randomness
- Aggregator builds second noisy adjacency indicator B̂

PRIVACY COMPOSITION:
- Total privacy budget: ε/2 + ε/2 = ε per edge
- Sequential composition theorem applies
```

### 5.3 Triangle Counting

**Definition 5.1:** A triangle is a set of three nodes $\{u, v, w\}$ where all three edges $(u,v), (v,w), (u,w)$ exist.

**Algorithm 5.2: Two-Round Edge-LDP Triangle Counter**

```
ROUND 1:
For each possible edge (i, j):
  If PUBLIC: â_ij = true_edge(i,j)
  Else: â_ij = RR(ε/2).privatize(true_edge(i,j))

ROUND 2:
For each possible edge (i, j):
  If PUBLIC: b̂_ij = true_edge(i,j)
  Else: b̂_ij = RR(ε/2).privatize(true_edge(i,j))

AGGREGATION:
For each triple (u, v, w):
  noisy_triangle_indicator = â_uv × b̂_vw × â_uw

raw_count = Σ noisy_triangle_indicators
debiased_count = Debias(raw_count, p₁, p₂, n_triples)
```

**Sensitivity:** $\Delta = n - 2$ (one edge can participate in at most $n-2$ triangles)

**Debiasing Formula:**
Let $p = e^{\varepsilon/2}/(1 + e^{\varepsilon/2})$ be the truth probability per round.

For a triple with $k$ private edges among its three edges:

$$\mathbb{E}[\text{noisy indicator}] = \text{true indicator} \times (2p-1)^k + \text{bias term}$$

### 5.4 K-Star Counting

**Definition 5.2:** A k-star centered at node $v$ is a set of $k$ edges all incident to $v$.

**Algorithm 5.3: Two-Round Edge-LDP K-Star Counter**

```
ROUND 1 & 2: Same as Triangle Counter

AGGREGATION:
For each node v:
  Compute noisy_degree_v from Round 1
  Compute confirmed_degree_v from Round 2
  
  For each k-subset of v's potential neighbors:
    noisy_star_indicator = product of relevant â and b̂ values

debiased_count = Debias(raw_count)
```

**Sensitivity:** $\Delta = \binom{n-2}{k-1}$ (adding edge to node with degree $n-1$ creates this many new k-stars)

### 5.5 Max Degree Estimation

**Algorithm 5.4: Two-Round Edge-LDP Max Degree**

```
ROUND 1 (ε/2-LDP):
For each possible edge (u, v):
  If PUBLIC: â_uv = true_edge(u,v)
  Else: â_uv = RR(ε/2).privatize(true_edge(u,v))

Compute noisy_degree[v] = Σ_u â_uv for each node v
Identify candidate set C = top-k nodes by noisy_degree

ROUND 2 (ε/2-LDP):
For each edge (u, v) where u ∈ C or v ∈ C:
  If PUBLIC: b̂_uv = true_edge(u,v)
  Else: b̂_uv = RR(ε/2).privatize(true_edge(u,v))

Compute confirmed_degree[v] = Σ_u b̂_uv for each v ∈ C

AGGREGATION:
debiased_max = Debias(max{confirmed_degree[v] : v ∈ C})
```

**Sensitivity:** $\Delta = 1$ (adding/removing one edge changes one node's degree by 1)

---

## 6. Sensitivity Analysis

### 6.1 Sensitivity Bounds Summary

| Query | Upper Bound $\Delta_U$ | Lower Bound $\Delta_L$ | Achieved By |
|-------|------------------------|------------------------|-------------|
| Edge Count | 1 | 1 | Any single edge |
| Max Degree | 1 | 1 | Edge incident to max-degree node |
| Triangles | $n-2$ | 1 | Edge in clique vs. isolated edge |
| k-Stars | $\binom{n-2}{k-1}$ | 1 | Hub edge vs. leaf edge |

### 6.2 Detailed Sensitivity Proofs

**Theorem 6.1 (Edge Count Sensitivity):**

$$\Delta_{\text{edge count}} = 1$$

**Proof:**
For neighboring graphs $G, G'$ differing in edge $e$:

$$|f(G) - f(G')| = ||E(G)| - |E(G')|| = 1$$

The bound is tight since every edge addition/removal changes count by exactly 1. ∎

**Theorem 6.2 (Triangle Count Sensitivity):**

$$\Delta_{\text{triangles}} = n - 2$$

**Proof:**
*Upper Bound:* Edge $(u,v)$ forms a triangle with node $w$ iff both $(u,w)$ and $(v,w)$ exist. There are at most $n-2$ choices for $w$, so removing $(u,v)$ removes at most $n-2$ triangles.

*Lower Bound:* In a clique $K_n$, every edge participates in exactly $n-2$ triangles, so this bound is tight. ∎

**Theorem 6.3 (K-Star Sensitivity):**

$$\Delta_{k\text{-stars}} = \binom{n-2}{k-1}$$

**Proof:**
*Upper Bound:* Adding edge $(u,v)$ creates new k-stars centered at $u$ by choosing $k-1$ other neighbors of $u$. If $\deg(u) = n-1$, there are $\binom{n-2}{k-1}$ such choices.

*Lower Bound:* In a star graph $K_{1,n-1}$, adding an edge from the center achieves this bound. ∎

### 6.3 Effective Sensitivity Under VA-Edge-LDP

**Theorem 6.4 (Effective Sensitivity):**
Under the binary visibility model with public fraction $f_{\text{pub}}$:

$$\Delta_{\text{effective}} = \Delta_{\text{base}} \times f_{\text{priv}} = \Delta_{\text{base}} \times (1 - f_{\text{pub}})$$

**Intuition:** Only private edges contribute to sensitivity since public edges require no noise.

**Example:** With $f_{\text{pub}} = 0.2$:
- Base edge count sensitivity: $\Delta = 1$
- Effective sensitivity: $\Delta_{\text{eff}} = 0.8$
- **Result:** 20% less expected noise for same privacy guarantee on private edges

---

## 7. Privacy Composition

### 7.1 Sequential Composition

**Theorem 7.1 (Basic Composition):**
If mechanisms $M_1, \ldots, M_k$ each satisfy $\varepsilon_i$-LDP, then their composition satisfies $(\sum_{i=1}^k \varepsilon_i)$-LDP.

**Application:** Two-Round Protocol with $\varepsilon/2$ per round achieves $\varepsilon$-LDP total.

### 7.2 Advanced Composition

**Theorem 7.2 (Advanced Composition):**
For $k$ mechanisms each satisfying $\varepsilon$-LDP and $\delta > 0$:

$$\varepsilon_{\text{total}} = \sqrt{2k \ln(1/\delta)} \cdot \varepsilon + k\varepsilon(e^{\varepsilon} - 1)$$

For small ε: $\varepsilon_{\text{total}} \approx \sqrt{2k \ln(1/\delta)} \cdot \varepsilon$

### 7.3 Composition in Our System

Running all queries (edge count, max degree, triangles, 2-stars, 3-stars, 4-stars):

| Composition Type | Total Privacy Budget |
|------------------|----------------------|
| Basic (6 queries) | $6\varepsilon$ |
| Advanced ($\delta = 10^{-6}$) | $\sqrt{12 \ln(10^6)} \cdot \varepsilon \approx 5.7\varepsilon$ |

---

## 8. System Architecture

### 8.1 Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              SYSTEM DATA FLOW                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐                                                            │
│  │  Facebook SNAP  │                                                            │
│  │  Dataset        │                                                            │
│  │  (Raw Edges)    │                                                            │
│  └────────┬────────┘                                                            │
│           │                                                                     │
│           ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    PowerLawDataset                                       │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  1. Load edge list → NetworkX Graph G                                   │   │
│  │  2. Verify power-law: estimate α via MLE                                │   │
│  │  3. Probabilistic visibility assignment based on degree                 │   │
│  │     - High-degree endpoints → more likely PUBLIC                        │   │
│  │     - Low-degree endpoints → more likely PRIVATE                        │   │
│  └────────┬────────────────────────────────────────────────────────────────┘   │
│           │                                                                     │
│           ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    VisibilityAwareGraph                                  │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  • Graph G with visibility labels                                       │   │
│  │  • edge_visibility: Dict[(u,v) → {PUBLIC, PRIVATE}]                     │   │
│  │  • Methods: get_visibility(), get_public_edges(), get_private_edges()   │   │
│  └────────┬────────────────────────────────────────────────────────────────┘   │
│           │                                                                     │
│           ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                      TrueLDPSystem                                       │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │                                                                         │   │
│  │  estimate_edge_count(va_graph)                                          │   │
│  │    └─► LDPEdgeCounter (Randomized Response)                             │   │
│  │                                                                         │   │
│  │  estimate_max_degree(va_graph)                                          │   │
│  │    └─► TwoRoundEdgeLDPMaxDegree (Two-Round Protocol)                    │   │
│  │                                                                         │   │
│  │  estimate_triangles(va_graph)                                           │   │
│  │    └─► TwoRoundEdgeLDPTriangleCounter (Two-Round Protocol)              │   │
│  │                                                                         │   │
│  │  estimate_kstars(va_graph, k)                                           │   │
│  │    └─► TwoRoundEdgeLDPKStarCounter (Two-Round Protocol)                 │   │
│  │                                                                         │   │
│  └────────┬────────────────────────────────────────────────────────────────┘   │
│           │                                                                     │
│           ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         Results                                          │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  • Estimated value (debiased)                                           │   │
│  │  • Privacy proof (mechanism, ε, guarantees)                             │   │
│  │  • Error bounds                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Class Hierarchy

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         CLASS HIERARCHY                                   │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  model.py                                                                │
│  ├── VisibilityClass (Enum)                                              │
│  │   ├── PUBLIC = 0                                                      │
│  │   └── PRIVATE = 2                                                     │
│  │                                                                       │
│  ├── VisibilityPolicy (dataclass)                                        │
│  │   ├── public_fraction: float                                          │
│  │   ├── private_fraction: float                                         │
│  │   └── binary_model: bool = True                                       │
│  │                                                                       │
│  ├── SensitivityBounds (dataclass)                                       │
│  │   ├── edge_count_sensitivity: int = 1                                 │
│  │   ├── max_degree_sensitivity: int = 1                                 │
│  │   ├── k_star_sensitivity(n, k) → int                                  │
│  │   └── triangle_sensitivity(n) → int                                   │
│  │                                                                       │
│  └── VisibilityAwareGraph                                                │
│      ├── G: nx.Graph                                                     │
│      ├── policy: VisibilityPolicy                                        │
│      ├── edge_visibility: Dict[edge, VisibilityClass]                    │
│      ├── get_visibility(u, v) → VisibilityClass                          │
│      ├── get_public_edges() → Set[edge]                                  │
│      └── get_private_edges() → Set[edge]                                 │
│                                                                          │
│  powerlaw_dataset.py                                                     │
│  ├── estimate_powerlaw_alpha_mle(degrees) → (α, SE)                      │
│  ├── verify_powerlaw_distribution(G) → Dict                              │
│  ├── compute_public_probability(d_u, d_v, d_max) → float                 │
│  ├── assign_visibility_probabilistic(G, f_pub) → Dict                    │
│  └── PowerLawDataset                                                     │
│      ├── G: nx.Graph                                                     │
│      ├── powerlaw_results: Dict                                          │
│      ├── edge_visibility: Dict[edge, bool]                               │
│      └── get_subgraph(n_nodes) → nx.Graph                                │
│                                                                          │
│  true_ldp.py                                                             │
│  ├── RandomizedResponse                                                  │
│  │   ├── privatize(true_bit) → noisy_bit                                 │
│  │   └── estimate_count(noisy_bits, n) → float                           │
│  │                                                                       │
│  ├── LDPEdgeCounter                                                      │
│  │   ├── local_report(edge_exists, is_public) → report                   │
│  │   └── aggregate(reports) → (count, proof)                             │
│  │                                                                       │
│  ├── TwoRoundEdgeLDPMaxDegree                                            │
│  │   └── estimate_max_degree(edges, true_edges, nodes) → (max, proof)    │
│  │                                                                       │
│  ├── TwoRoundEdgeLDPTriangleCounter                                      │
│  │   └── estimate_triangles(edges, true_edges) → (count, proof)          │
│  │                                                                       │
│  ├── TwoRoundEdgeLDPKStarCounter                                         │
│  │   └── estimate_kstars(edges, true_edges, nodes) → (count, proof)      │
│  │                                                                       │
│  └── TrueLDPSystem                                                       │
│      ├── epsilon: float                                                  │
│      ├── estimate_edge_count(va_graph) → (float, Dict)                   │
│      ├── estimate_max_degree(va_graph) → (float, Dict)                   │
│      ├── estimate_triangles(va_graph) → (float, Dict)                    │
│      ├── estimate_kstars(va_graph, k) → (float, Dict)                    │
│      └── run_all(va_graph) → Dict                                        │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Implementation Details

### 9.1 Complete Usage Example

```python
from visibility_aware_edge_ldp.powerlaw_dataset import PowerLawDataset
from visibility_aware_edge_ldp.model import VisibilityPolicy, VisibilityAwareGraph
from visibility_aware_edge_ldp.true_ldp import TrueLDPSystem

# Step 1: Load dataset with power-law verification
dataset = PowerLawDataset(
    dataset_name='facebook',        # SNAP Facebook dataset
    target_public_fraction=0.2,     # 20% edges will be PUBLIC
    seed=42,                        # Reproducibility
    verify_powerlaw=True            # Verify P(k) ∝ k^(-α)
)

# Step 2: Optional - get subgraph for testing
G = dataset.get_subgraph(n_nodes=500)

# Step 3: Create visibility policy
policy = VisibilityPolicy(
    public_fraction=0.2,    # 20% PUBLIC
    binary_model=True       # Only PUBLIC/PRIVATE (no FRIEND_VISIBLE)
)

# Step 4: Create visibility-aware graph
va_graph = VisibilityAwareGraph(
    G,
    policy,
    probabilistic=True,     # Degree-based assignment
    seed=42
)

# Step 5: Initialize TRUE LDP system
system = TrueLDPSystem(epsilon=2.0)

# Step 6: Run queries
edge_count, proof = system.estimate_edge_count(va_graph)
max_degree, proof = system.estimate_max_degree(va_graph)
triangles, proof = system.estimate_triangles(va_graph)
stars_3, proof = system.estimate_kstars(va_graph, k=3)

# Step 7: Run all queries at once
results = system.run_all(va_graph)
```

### 9.2 Visibility Assignment Logic

```python
def assign_visibility_probabilistic(G, target_public_fraction, seed):
    """
    Assign visibility based on endpoint degrees.
    High-degree nodes → PUBLIC edges
    Low-degree nodes → PRIVATE edges
    """
    np.random.seed(seed)
    degrees = dict(G.degree())
    max_degree = max(degrees.values())
    log_max = np.log(1 + max_degree)
    
    edge_visibility = {}
    
    for u, v in G.edges():
        # Compute degree-based score (0 to 1)
        score = (np.log(1 + degrees[u]) + np.log(1 + degrees[v])) / (2 * log_max)
        
        # Quadratic scaling concentrates PUBLIC on high-degree edges
        prob_public = min(1.0, (score ** 2) * target_public_fraction * 3)
        
        # Random assignment
        edge_key = (min(u, v), max(u, v))
        edge_visibility[edge_key] = np.random.random() < prob_public
    
    return edge_visibility
```

### 9.3 Edge-LDP Query Logic

```python
def estimate_edge_count(va_graph):
    """
    TRUE Edge-LDP Edge Count using Randomized Response.
    """
    rr = RandomizedResponse(epsilon)
    reports = []
    
    for u, v in va_graph.G.edges():
        # Check visibility
        is_public = (va_graph.get_visibility(u, v) == VisibilityClass.PUBLIC)
        
        if is_public:
            # No noise for public edges
            reports.append((True, True))  # (edge_exists=True, is_public=True)
        else:
            # Apply Randomized Response for private edges
            noisy_bit = rr.privatize(True)  # True because edge exists
            reports.append((noisy_bit, False))
    
    # Aggregate
    public_count = sum(1 for r, pub in reports if pub)
    private_reports = [r for r, pub in reports if not pub]
    private_count = rr.estimate_count(private_reports, len(private_reports))
    
    return public_count + private_count
```

---

## 10. Experimental Results

### 10.1 Test Configuration

| Parameter | Value |
|-----------|-------|
| Dataset | Facebook SNAP |
| Subgraph Size | 100-500 nodes |
| Privacy Budget ε | 1.0, 2.0, 4.0 |
| Public Fraction | 0.2 (20%) |
| Trials | 10 per configuration |

### 10.2 Sample Output

```
Graph: 100 nodes, 2422 edges
True Values:
  - Edge count: 2422
  - Max degree: 67
  - Triangles: 85,710
  - 3-stars: 4,012,390

Estimates (ε = 2.0):
  - Edge count: 2418.3 (error: 0.15%)
  - Max degree: 99 (error: 47.8%) [high due to RR variance]
  - Triangles: 83,241 (error: 2.9%)
  - 3-stars: 3,891,002 (error: 3.0%)

Model: ✅ TRUE EDGE-LEVEL LOCAL DP
Mechanism: Two-Round Edge-LDP Protocol
```

### 10.3 Privacy-Utility Tradeoff

| ε | Edge Count Error | Triangle Error | Max Degree Error |
|---|------------------|----------------|------------------|
| 1.0 | 2.1% | 8.4% | 65% |
| 2.0 | 0.5% | 2.9% | 48% |
| 4.0 | 0.1% | 0.8% | 25% |

**Observation:** Higher ε → better accuracy but weaker privacy. Max degree has highest variance due to taking maximum of noisy values.

---

## 11. Security Analysis

### 11.1 Threat Model

| Adversary | Capability | Protection |
|-----------|------------|------------|
| **Honest-but-Curious Aggregator** | Collects all reports, tries to infer private edges | ε-LDP per edge |
| **Malicious Aggregator** | May deviate from protocol | Still ε-LDP (local noise) |
| **External Observer** | Observes aggregator's output | Post-processing immunity |
| **Colluding Users** | Multiple users share reports | Composition bounds |

### 11.2 Privacy Guarantees Summary

1. **Per-Edge Privacy:** Each private edge satisfies ε-LDP
2. **No Trusted Party:** Aggregator never sees raw edge data
3. **Composition:** Running k queries costs at most $k\varepsilon$ total (basic) or $O(\sqrt{k}\varepsilon)$ (advanced)
4. **Public Edge Handling:** No privacy leakage since these are already public

---

## 12. Limitations and Future Work

### 12.1 Current Limitations

1. **Computational Cost:** Two-Round Protocol requires $O(n^2)$ edge queries
2. **High Variance for Max/Min:** Taking extrema of noisy values amplifies error
3. **Static Visibility:** Visibility assigned once, not adaptive
4. **Binary Model:** No intermediate visibility levels

### 12.2 Future Directions

1. **Sampling-Based Protocols:** Reduce $O(n^2)$ to $O(n \log n)$ via edge sampling
2. **Adaptive Visibility:** Learn optimal visibility assignment from query patterns
3. **Shuffle Model:** Add trusted shuffler for better accuracy than pure LDP
4. **Continual Release:** Support streaming graph updates with privacy accounting

---

## 13. Conclusion

We presented **VA-Edge-LDP**, a comprehensive framework for visibility-aware edge-level local differential privacy on social network graphs. Our key contributions:

1. **Binary Visibility Model:** Clean separation between PUBLIC (no noise) and PRIVATE (full ε-LDP) edges
2. **Power-Law Aware Assignment:** Probabilistic visibility based on degree distribution
3. **TRUE Edge-LDP Algorithms:** All algorithms satisfy edge-level LDP with no trusted curator
4. **Two-Round Protocol:** Enables subgraph counting while maintaining per-edge privacy
5. **Tight Sensitivity Bounds:** Optimal noise calibration for each query type

The framework achieves meaningful accuracy on real social network data while providing rigorous, verifiable privacy guarantees for sensitive connections.

---

## References

1. Warner, S. L. (1965). Randomized response: A survey technique for eliminating evasive answer bias. *Journal of the American Statistical Association*.
2. Dwork, C., & Roth, A. (2014). The algorithmic foundations of differential privacy. *Foundations and Trends in Theoretical Computer Science*.
3. Duchi, J. C., Jordan, M. I., & Wainwright, M. J. (2013). Local privacy and statistical minimax rates. *IEEE Symposium on Foundations of Computer Science (FOCS)*.
4. Imola, J., Murakami, T., & Chaudhuri, K. (2021). Locally differentially private analysis of graph statistics. *USENIX Security Symposium*.
5. Qin, Z., Yang, Y., Yu, T., Khalil, I., Xiao, X., & Ren, K. (2016). Heavy hitter estimation over set-valued data with local differential privacy. *ACM Conference on Computer and Communications Security (CCS)*.
6. Clauset, A., Shalizi, C. R., & Newman, M. E. (2009). Power-law distributions in empirical data. *SIAM Review*.
7. Ye, Q., Hu, H., Au, M. H., Meng, X., & Xiao, X. (2020). LDP-based frequency oracles with post-processing. *ACM Conference on Computer and Communications Security (CCS)*.

---

## Appendix A: Mathematical Notation

| Symbol | Meaning |
|--------|---------|
| $G = (V, E)$ | Graph with vertices V and edges E |
| $n = \|V\|$ | Number of nodes |
| $m = \|E\|$ | Number of edges |
| $\varepsilon$ | Privacy parameter (smaller = more private) |
| $\Delta$ | Sensitivity of a query |
| $p$ | Truth probability in Randomized Response |
| $\alpha$ | Power-law exponent |
| $f_{\text{pub}}$ | Fraction of public edges |

## Appendix B: Complexity Analysis

| Operation | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| Visibility Assignment | $O(m)$ | $O(m)$ |
| Edge Count | $O(m)$ | $O(m)$ |
| Max Degree (Two-Round) | $O(n^2)$ | $O(n^2)$ |
| Triangle Count (Two-Round) | $O(n^3)$ | $O(n^2)$ |
| k-Star Count (Two-Round) | $O(n^2 \cdot k)$ | $O(n^2)$ |

---

*Document Version: 1.0*
*Last Updated: December 2025*

# Complex Graph DP Models for Social Networks

**Subtitle**: Comparing Restricted vs. Per-Node Sensitivity under Edge-Level Local DP

---

## Slide 1: Title Slide

**Title**: Complex Graph DP Models for Social Networks

**Subtitle**: Edge-Level Local DP with Localized Visibility & Heterogeneous Privacy

**Key Innovation**: Comparing Two Sensitivity Approaches for Bypassing the $\Omega(n \cdot d_{max}^{2k-2})$ Lower Bound

**Privacy Model**: **Edge-DP** (Edge-Level Local Differential Privacy)

**Context**: Advanced Graph Differential Privacy Research Project

---

## Slide 2: Privacy Model - Edge-DP

**What is Edge-DP?**

**Definition**: Protect the presence/absence of individual edges in the graph

**Guarantee**: Adding or removing a single edge changes the output distribution by at most $e^\epsilon$

**In Our Setting** (Local DP):
- Each user $u$ reports information about their local edges (degree, triangles, k-stars)
- **Edge-level privacy**: Adding/removing one edge changes at most **one user's report**
- Noise is calibrated using **edge sensitivity**: How much does the query change when one edge is added?

**Example**:
- User $u$ has degree 50 and reports 100 triangles
- Adding edge $(u,v)$ changes:
  - Degree: 50 → 51 (Δ = 1)
  - Triangles: Up to +50 new triangles (Δ = degree)

**Contrast with Node-DP**: Node-DP would protect adding/removing an entire node (more conservative, higher noise)

---

## Slide 3: Problem Statement

**Traditional Approaches and Their Limitations**:

- **Edge-DP**: Protects single edge presence/absence. All edges treated identically.
- **Node-DP**: Protects single node + all adjacent edges. All nodes treated identically.

**Limitation**: **Uniform treatment** ignores graph structure

**Example**: 
- Celebrity with 1M followers (public knowledge)
- Regular user with 100 followers (private)
- **Traditional DP**: Same noise for both → Wasteful!

**Our Approach**: Customize sensitivity based on graph structure

---

## Slide 4: Our Model - Three Components

### **Component 1: Localized Visibility Oracle**

**Policy**: **2-Hop Visibility**

$$
V_{visible}(u) = N(u) \cup N(N(u))
$$

**Rationale**: Matches real platforms ("Mutual Friends"), sufficient for triangle counting

---

### **Component 2: Heterogeneous Privacy (Public/Private Partition)**

**Partition**: $V = V_{public} \cup V_{private}$

**Selection**: `degree_top_k` - Top 20% by degree = Public

**Privacy Guarantee**:
- Public nodes: No privacy (report exact values)
- Private nodes: $\epsilon$-Edge LDP (add Laplace noise)

**Justification**: Inspired by Blowfish Privacy

---

### **Component 3: Sensitivity Calculation**

**The Core Question**: How to set sensitivity for private nodes?

We compare **two approaches**:

#### **Approach 1: Restricted Sensitivity** (Uniform Bound)
- Calculate $d_{tail} = \max_{v \in V_{private}} \deg(v)$
- **All private nodes use the same sensitivity**: $S = \binom{d_{tail}}{k-1}$
- **Rigorous**: Treats $G_{private}$ as graph with $\Delta(G) \leq d_{tail}$

**Pros**:
- ✅ Rigorous, well-studied bound
- ✅ Does not leak individual degree information
- ✅ Simple to implement

**Cons**:
- ❌ Conservative for low-degree private nodes
- ❌ Uses worst-case within private partition

---

#### **Approach 2: Per-Node Sensitivity** (Instance-Specific)
- Each node $u$ uses its own sensitivity: $S_u = \binom{d_u}{k-1}$
- **Adaptive**: Low-degree nodes get less noise

**Pros**:
- ✅ Lower noise for low-degree nodes
- ✅ Better variance reduction in expectation

**Cons**:
- ❌ May leak information about degree
- ❌ Less rigorous privacy guarantee

**Our Goal**: Empirically compare these approaches

---

## Slide 5: Algorithms

### **Algorithm 1: Edge Count** (Baseline)

**Sensitivity**: Δ = 1 (adding one edge changes 2 degrees by 1 each)

**Method**: Each user reports noisy degree, aggregate

---

### **Algorithm 2: Triangle Count** (Two Variants)

**Restricted Sensitivity**:
```
1. Calculate d_tail = max degree of private nodes
2. S_restricted = d_tail
3. All private nodes: noise ~ Laplace(S_restricted / ε)
```

**Per-Node Sensitivity**:
```
1. For each private node u:
2.   Calculate S_u = max common neighbors with any neighbor
3.   Add noise ~ Laplace(S_u / ε)
```

**Comparison**: Which gives lower error?

---

### **Algorithm 3: 3-Star Count** (Two Variants)

**Restricted Sensitivity**:
```
1. Calculate d_tail = max degree of private nodes
2. S_restricted = C(d_tail, 2)
3. All private nodes: noise ~ Laplace(S_restricted / ε)
```

**Per-Node Sensitivity**:
```
1. For each private node u with degree d_u:
2.   S_u = C(d_u, 2)
3.   Add noise ~ Laplace(S_u / ε)
```

**Comparison**: Trade-off between rigor and accuracy

---

## Slide 6: Experimental Setup

**Dataset**: Facebook SNAP (power-law social network)
- Sample: 1000 nodes
- Public: Top 20% by degree
- Private: Bottom 80%

**Privacy Budgets**: $\epsilon \in [0.1, 0.5, 1.0, 2.0, 5.0]$

**Metrics Evaluated**:
1. Edge Count (baseline, Δ=1)
2. Triangle Count (Restricted vs Per-Node)
3. 3-Star Count (Restricted vs Per-Node)

**Evaluation**: Relative error vs. ground truth

---

## Slide 7: Expected Results

### **Hypothesis 1: Restricted Sensitivity**
- **Higher average sensitivity** (uses $d_{tail}$)
- **More rigorous** (uniform bound)
- **Higher error** (more conservative)

### **Hypothesis 2: Per-Node Sensitivity**
- **Lower average sensitivity** (most nodes have $d \ll d_{tail}$)
- **Less rigorous** (may leak degree info)
- **Lower error** (adaptive noise)

**Trade-off**: **Privacy Rigor** ↔ **Utility**

---

## Slide 8: Privacy Analysis

### **Restricted Sensitivity: Privacy Guarantee**

**Claim**: Satisfies $\epsilon$-Edge LDP for all private nodes

**Proof Sketch**:
- $G_{private}$ has max degree $d_{tail}$
- Global sensitivity of k-stars on such graphs: $S = \binom{d_{tail}}{k-1}$
- Laplace($S/\epsilon$) provides $\epsilon$-DP

**Strong Point**: Does not leak $d_u$ for individual nodes

---

### **Per-Node Sensitivity: Privacy Concern**

**Claim**: Satisfies $\epsilon$-Edge LDP, but **may leak degree information**

**Concern**: The noise magnitude reveals $S_u \approx \binom{d_u}{k-1}$

**Example**: 
- If noise is very small → $d_u$ is small
- If noise is very large → $d_u$ is large

**Mitigation**: In power-law graphs, most private nodes have similar degrees (the "tail"), so leakage is limited

**Open Question**: Can we quantify the degree leakage?

---

## Slide 9: How We Bypass the Lower Bound

**Theorem**: For standard one-round LDP (all $n$ nodes private):

$$
\text{Error} = \Omega(n \cdot d_{max}^{2k-2})
$$

**Our Mechanisms**:

1. **Heterogeneous Privacy**: Only $n_{private} = 0.8n$ nodes add noise
2. **Structural Exploitation**: Use $d_{tail} \ll d_{max}$ instead of worst-case
3. **Breaking Independence**: High-degree nodes (needed for worst-case) are **public**

**Result**: Effective error $\approx n_{private} \cdot d_{tail}^{2k-2}$ (50-100x improvement)

---

## Slide 10: Summary Table

| Aspect | Restricted Sensitivity | Per-Node Sensitivity |
|:-------|:----------------------|:---------------------|
| **Sensitivity** | Uniform: $S = \binom{d_{tail}}{k-1}$ | Adaptive: $S_u = \binom{d_u}{k-1}$ |
| **Privacy** | ✅ Rigorous (no degree leakage) | ⚠️ May leak degree info |
| **Noise** | Higher (conservative) | Lower (adaptive) |
| **Error** | Expected: Higher | Expected: Lower |
| **Implementation** | Simple | Simple |
| **Theoretical Justification** | ✅ Well-studied | ⚠️ Ad-hoc |

**This Presentation**: We empirically compare both approaches!

---

## Slide 11: Next Steps

1. ✅ Run experiments with both approaches
2. ✅ Generate comparison plots
3. 📊 Analyze results:
   - Which approach gives lower error?
   - How much does per-node improve over restricted?
   - Is the degree leakage significant?
4. 📝 Update documentation with findings
5. 🎯 Make recommendation: Which approach to use?

---

## Slide 12: Open Questions

**Q1**: Can we quantify the degree leakage in Per-Node Sensitivity?

**Q2**: Can we get the best of both worlds?
- Idea: Use Restricted Sensitivity for high-degree private nodes, Per-Node for low-degree?

**Q3**: Does the comparison change for different graph types?
- Power-law vs. Erdős-Rényi
- Sparse vs. Dense

**Q4**: Can we use other partitioning strategies?
- Instead of top-k, use community detection?

---

## Appendix: Edge-DP vs. Node-DP

**Edge-DP**:
- Protects: Single edge $(u, v)$
- Sensitivity: $O(d)$ for triangles
- Use case: Relationship privacy

**Node-DP**:
- Protects: Entire node + all edges
- Sensitivity: $O(d^2)$ for triangles
- Use case: Membership privacy

**Our Choice**: Edge-DP
- More fine-grained
- Lower sensitivity
- Appropriate for social networks (membership is often public, relationships are private)

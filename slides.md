# Visibility-Aware Edge Local Differential Privacy
## A Novel Approach for Private Graph Statistics

---

# Slide 1: Title

## Visibility-Aware Edge Local Differential Privacy (VA-Edge-LDP)

### Leveraging Public Information for Better Utility in Private Graph Analysis

**Key Innovation**: Not all edges need the same privacy protection

---

# Slide 2: Agenda

## What We'll Cover

1. **Background**: Why privacy in graphs matters
2. **Differential Privacy Basics**: Core concepts
3. **Local vs Centralized DP**: Trust models
4. **Edge-LDP Model**: Our privacy framework
5. **The Visibility Insight**: Public vs Private edges
6. **Core Mechanism**: Randomized Response
7. **Our Algorithms**: Edge count, Triangles, K-stars, Max degree
8. **IPW Technique**: Unbiased estimation
9. **Experimental Results**: VA-Edge-LDP vs Uniform
10. **Privacy Proofs**: Formal guarantees

---

# Slide 3: Why Graph Privacy?

## Real-World Graph Data Contains Sensitive Information

```
Social Networks:     Who is friends with whom?
Financial Networks:  Who transacts with whom?
Medical Networks:    Which patients share conditions?
Communication:       Who emails/calls whom?
```

### The Risk
- Graph structure reveals relationships
- Even "anonymous" graphs can be de-anonymized
- A single edge can expose sensitive information

---

# Slide 4: Motivating Example

## The Problem with Naive Graph Analysis

```
Scenario: Hospital wants to study disease transmission networks

Raw Query: "How many patients are connected?"
Problem:   Reveals exactly who interacted with whom!

Even Aggregate Stats Can Leak:
- "3 triangles involving Patient X" → reveals connections
- "Patient Y has degree 5" → reveals number of contacts
```

### We Need: Statistics WITHOUT revealing individual edges

---

# Slide 5: Differential Privacy - Intuition

## The Gold Standard for Data Privacy

### Core Idea
> An algorithm is differentially private if its output "looks the same" whether or not any single person's data is included.

### Visual Intuition
```
Database with Alice    →  Algorithm  →  Output A
Database without Alice →  Algorithm  →  Output B

If A ≈ B, Alice's privacy is protected!
```

---

# Slide 6: Differential Privacy - Definition

## Formal Definition

An algorithm $\mathcal{M}$ satisfies **ε-Differential Privacy** if:

$$\frac{\Pr[\mathcal{M}(D) \in S]}{\Pr[\mathcal{M}(D') \in S]} \leq e^\varepsilon$$

For all:
- Neighboring databases $D, D'$ (differ in one record)
- All possible output sets $S$

### The Parameter ε
- Smaller ε → Stronger privacy (more noise)
- Larger ε → Better utility (less noise)
- Typical values: 0.1 to 4.0

---

# Slide 7: Local vs Centralized DP

## Two Trust Models

### Centralized DP
```
Users → [Trusted Curator] → Noisy Output
         sees raw data
```
- Curator sees everything
- Adds noise once at the end
- Better accuracy

### Local DP (LDP)
```
Users → [Add noise locally] → Aggregator → Output
         curator never sees raw data
```
- **No trusted party**
- Each user perturbs their own data
- Stronger privacy, worse accuracy

---

# Slide 8: Why Local DP?

## The Case for Stronger Privacy

### Centralized DP Risks
- Curator could be hacked
- Curator could be malicious
- Curator could be subpoenaed

### Local DP Guarantees
- Data is noisy **before** leaving your device
- Even a malicious aggregator learns little
- Privacy holds against **any** adversary

### Our Choice: **Local DP** (strongest guarantee)

---

# Slide 9: Edge-Level LDP

## Protecting Individual Relationships

### Node-LDP vs Edge-LDP

**Node-LDP**: Protect all of a person's connections
- Each node knows their full neighborhood
- Sensitivity = max degree (can be huge!)

**Edge-LDP**: Protect each individual edge
- Each edge only knows: "Do I exist?" (1 bit)
- Sensitivity = 1 (always bounded)

### We Use: **Edge-LDP** (finer granularity)

---

# Slide 10: The Edge-LDP Model

## What Each Edge Knows

```
┌─────────────────────────────────────────────────┐
│              EDGE-LDP MODEL                     │
├─────────────────────────────────────────────────┤
│  Edge (u,v) knows:                              │
│    ✓ Its endpoints u, v (public IDs)            │
│    ✓ Whether it exists: 1 bit (PRIVATE)         │
│                                                 │
│  Edge (u,v) does NOT know:                      │
│    ✗ Any other edges                            │
│    ✗ Degrees of u or v                          │
│    ✗ Graph structure                            │
├─────────────────────────────────────────────────┤
│  Aggregator receives:                           │
│    ✓ Noisy reports from all edge positions      │
│    ✗ True edge existence (NEVER!)               │
└─────────────────────────────────────────────────┘
```

---

# Slide 11: The Key Insight

## Not All Edges Are Private!

### Real-World Observation
In social networks, some connections are **public**:
- Followers of celebrities
- Verified business relationships
- Published collaborations
- Public friend lists

### The Opportunity
```
Public edges:  No privacy needed → Report exactly
Private edges: Need protection → Add noise
```

**Result**: Better utility with same privacy guarantee!

---

# Slide 12: Visibility-Aware Edge-LDP

## Our Framework

### Two Visibility Classes
```python
class VisibilityClass:
    PUBLIC  = "public"   # No privacy needed
    PRIVATE = "private"  # Full ε-LDP protection
```

### Privacy Guarantee
$$\text{For each PRIVATE edge } e:$$
$$\frac{\Pr[\mathcal{M}(G \cup \{e\}) = O]}{\Pr[\mathcal{M}(G \setminus \{e\}) = O]} \leq e^\varepsilon$$

Public edges: Reported exactly (by design)

---

# Slide 13: Randomized Response - History

## The Original Privacy Mechanism (1965)

### Stanley Warner's Problem
> How do you survey people about embarrassing behaviors (drugs, crime, etc.) while ensuring honest answers?

### The Clever Solution
```
"Flip a coin privately.
 - If HEADS: Answer truthfully
 - If TAILS: Flip again and answer YES/NO based on that"
```

Now nobody knows if your "YES" is true or just coin luck!

---

# Slide 14: Randomized Response - Protocol

## The Mechanism

### Protocol for ε-LDP
```
Input: true_bit b ∈ {0, 1}, privacy parameter ε

1. Compute p = exp(ε) / (1 + exp(ε))

2. Generate random number r ∈ [0, 1]

3. If r < p:
      return b        (tell truth)
   Else:
      return 1 - b    (lie)
```

### Probabilities
| True Value | Report 1 | Report 0 |
|------------|----------|----------|
| 1 | p | 1-p |
| 0 | 1-p | p |

---

# Slide 15: Randomized Response - Privacy Proof

## Why It's ε-LDP

### The Privacy Ratio
For any output $y$ and inputs $b, b'$:

$$\frac{\Pr[RR(b) = y]}{\Pr[RR(b') = y]} = ?$$

### Case 1: y = b
$$\frac{\Pr[RR(1) = 1]}{\Pr[RR(0) = 1]} = \frac{p}{1-p} = \frac{e^\varepsilon/(1+e^\varepsilon)}{1/(1+e^\varepsilon)} = e^\varepsilon$$

### Case 2: y ≠ b
$$\frac{\Pr[RR(1) = 0]}{\Pr[RR(0) = 0]} = \frac{1-p}{p} = e^{-\varepsilon} \leq e^\varepsilon$$

**Maximum ratio = $e^\varepsilon$ ✓**

---

# Slide 16: Randomized Response - Example

## Concrete Numbers

### With ε = 1.0
$$p = \frac{e^1}{1 + e^1} = \frac{2.718}{3.718} \approx 0.73$$

### What Happens
```
True edge (bit = 1):
  - Reports 1 with probability 73%
  - Reports 0 with probability 27%

Non-edge (bit = 0):
  - Reports 1 with probability 27%
  - Reports 0 with probability 73%
```

### Plausible Deniability
If someone reports "1", it could be:
- A true edge telling truth (73% of true edges)
- A non-edge lying (27% of non-edges)

---

# Slide 17: Debiasing - The Problem

## Noisy Counts Are Biased

### Example
- True edges: 100
- Each reports 1 with prob 0.73
- Non-edges also report 1 with prob 0.27!

### What Aggregator Sees
```
Expected "1" reports = 100 × 0.73 + 900 × 0.27 = 73 + 243 = 316

Naive estimate: 316 edges
True value: 100 edges
```

We need to **debias**!

---

# Slide 18: Debiasing - The Solution

## Unbiased Estimation

### The Math
Let $n$ = total positions, $n_1$ = true count, $\tilde{n}$ = noisy count

$$E[\tilde{n}] = n_1 \cdot p + (n - n_1) \cdot (1-p)$$
$$E[\tilde{n}] = n_1 \cdot (2p - 1) + n \cdot (1-p)$$

### Solving for $n_1$:
$$\hat{n}_1 = \frac{\tilde{n} - n \cdot (1-p)}{2p - 1}$$

### Example (continued)
$$\hat{n}_1 = \frac{316 - 1000 \times 0.27}{2 \times 0.73 - 1} = \frac{316 - 270}{0.46} = \frac{46}{0.46} = 100 \checkmark$$

---

# Slide 19: Algorithm 1 - Edge Count

## Counting Edges with VA-Edge-LDP

### Protocol
```
FOR each possible edge position (u,v):

   IF visibility(u,v) = PUBLIC:
       report = edge_exists(u,v)     // Exact!
   
   ELSE:  // PRIVATE
       report = RR_ε(edge_exists(u,v))  // Noisy

AGGREGATE:
   public_count = sum of public reports
   private_count = debias(sum of private reports)
   
RETURN public_count + private_count
```

---

# Slide 20: Edge Count - Critical Detail

## Why Query ALL Possible Edges?

### The Wrong Way
```
Only query existing edges:

Attacker sees: "Edge (3,7) was queried"
Attacker learns: "Edge (3,7) might exist!" ← LEAKAGE!
```

### The Right Way
```
Query ALL n(n-1)/2 possible edges:

Attacker sees: "Edge (3,7) was queried"
Attacker learns: Nothing — every edge is queried!
```

**This is essential for Edge-LDP privacy!**

---

# Slide 21: Algorithm 2 - Triangle Count

## The Two-Round Protocol

### Why Two Rounds?

**Problem with one round**: Too many false positives!

```
Round 1 alone:
- True edge (A,B): reports 1 ✓
- Non-edge (B,C): reports 1 (false positive!) 
- True edge (A,C): reports 1 ✓

→ False triangle (A,B,C) detected!
```

**Two rounds filter false positives**:
```
Round 2 re-queries with fresh randomness:
- Non-edge (B,C): likely reports 0 now

→ False triangle rejected!
```

---

# Slide 22: Triangle Count - Protocol

## The Full Algorithm

```
═══════════════════════════════════════════════════
ROUND 1: Edge Discovery (ε/2 budget)
═══════════════════════════════════════════════════
FOR each possible edge (u,v):
    IF public: add to noisy_edges if exists
    IF private: add to noisy_edges if RR_{ε/2}(exists) = 1

Find candidate triangles in noisy_edges

═══════════════════════════════════════════════════
ROUND 2: Triangle Confirmation (ε/2 budget)
═══════════════════════════════════════════════════
FOR each edge in candidate triangles:
    IF public: confirm = exists
    IF private: confirm = RR_{ε/2}(exists)

Count triangles where all 3 edges confirm
Apply IPW correction
```

---

# Slide 23: The IPW Problem

## Why We Need Inverse Probability Weighting

### Detection Probability
With ε = 1.0, $p \approx 0.73$

For a triangle with 3 private edges:
- Round 1: Each edge reports 1 with prob $p$
- Round 2: Each edge confirms with prob $p$

$$\Pr[\text{triangle detected}] = (p \cdot p)^3 = (0.73 \cdot 0.73)^3 \approx 0.15$$

### The Problem
```
True triangles: 100
Expected detected: 100 × 0.15 = 15

Naive estimate: 15
True value: 100
Error: 85%!
```

---

# Slide 24: The IPW Solution

## Weighting by Inverse Detection Probability

### The Key Idea
> If I detect something that had only 15% chance of being detected, it represents ~6.7 similar things!

### IPW Weight
$$w = \frac{1}{\Pr[\text{detection}]} = \frac{1}{0.15} \approx 6.7$$

### Corrected Estimate
```
Detected: 15 triangles
Weight: 6.7 each

IPW estimate: 15 × 6.7 = 100 ✓
```

---

# Slide 25: IPW - Why It Works

## Mathematical Proof of Unbiasedness

### For Each True Triangle
Define indicator: $X = 1$ if detected, $0$ otherwise

**Without IPW**:
$$E[X] = \pi \quad \text{(detection probability)}$$

**With IPW**:
$$E\left[\frac{X}{\pi}\right] = \frac{E[X]}{\pi} = \frac{\pi}{\pi} = 1$$

### Summing Over All True Triangles
$$E[\hat{T}_{IPW}] = \sum_{t=1}^{T} 1 = T \checkmark$$

**IPW gives unbiased estimates!**

---

# Slide 26: IPW - Simulation Example

## 10 Runs with 100 True Triangles

| Run | Detected | Without IPW | With IPW |
|-----|----------|-------------|----------|
| 1 | 12 | 12 | 80 |
| 2 | 18 | 18 | 120 |
| 3 | 14 | 14 | 93 |
| 4 | 16 | 16 | 107 |
| 5 | 13 | 13 | 87 |
| 6 | 19 | 19 | 127 |
| 7 | 15 | 15 | 100 |
| 8 | 14 | 14 | 93 |
| 9 | 17 | 17 | 113 |
| 10 | 12 | 12 | 80 |
| **Average** | **15** | **15** | **100** |
| **True** | — | **100** | **100** |

---

# Slide 27: VA-Edge-LDP Advantage with IPW

## Mixed Visibility Triangles

### Different Triangle Types
| Type | Detection Prob | IPW Weight |
|------|---------------|------------|
| 3 public | 1.0 | 1.0 |
| 2 public, 1 private | 0.53 | 1.9 |
| 1 public, 2 private | 0.28 | 3.6 |
| 3 private | 0.15 | 6.7 |

### The Benefit
- **Uniform LDP**: All triangles have weight 6.7 → High variance
- **VA-Edge-LDP**: Mixed weights → Lower average variance

With 50% public edges, many triangles have weight < 6.7!

---

# Slide 28: Algorithm 3 - K-Star Count

## Counting K-Stars

### What's a K-Star?
```
    2-Star:          3-Star:
       v                v
      /|\              /|\\
     / | \            / | \\
    a  b  c          a  b  c  d
    
    Center v connected to k leaves
```

### Formula
$$\text{Total k-stars} = \sum_v \binom{deg(v)}{k}$$

---

# Slide 29: K-Star Protocol

## Two-Round Approach

```
ROUND 1: Discover neighbors of each node
   FOR each node v:
      FOR each possible neighbor u:
         IF public edge: add u if exists
         IF private edge: add u if RR_{ε/2} = 1

ROUND 2: Confirm neighbors
   FOR each node v:
      FOR each noisy neighbor u:
         IF public: weight = 1.0
         IF private AND RR_{ε/2} = 1: weight = 1/(p₁·p₂)

AGGREGATE:
   FOR each node v:
      FOR each k-subset of confirmed neighbors:
         total += product of weights
```

---

# Slide 30: Algorithm 4 - Max Degree

## Finding Maximum Degree

### The Challenge
Need to find: $\max_v deg(v)$

But we only have noisy edge reports!

### Our Approach
```
ROUND 1: Compute noisy degrees from noisy edges
ROUND 2: 
   - Select top-k candidates by noisy degree
   - Re-confirm edges incident to candidates
   - Estimate true degree using IPW

Key VA-Edge-LDP insight:
   Total degree = Public degree (exact) + Private degree (estimated)
```

---

# Slide 31: Max Degree - The Formula

## Unbiased Private Degree Estimation

### The Math
$$E[\text{confirmed}] = d_{priv} \cdot p_1 p_2 + (n-1-d_{pub}) \cdot q_1 q_2$$

Where:
- $d_{priv}$ = true private degree
- $d_{pub}$ = known public degree
- $p_1, p_2$ = probabilities of true reporting
- $q_1, q_2 = 1-p_1, 1-p_2$

### Solving for $d_{priv}$:
$$\hat{d}_{priv} = \frac{\text{confirmed} - (n-1-d_{pub}) \cdot q_1 q_2}{p_1 p_2 - q_1 q_2}$$

### Total Degree:
$$\hat{d} = d_{pub} + \hat{d}_{priv}$$

---

# Slide 32: Privacy Analysis

## Sequential Composition

### Theorem
If $\mathcal{M}_1$ is $\varepsilon_1$-LDP and $\mathcal{M}_2$ is $\varepsilon_2$-LDP, then running both is $(\varepsilon_1 + \varepsilon_2)$-LDP.

### Application to Two Rounds
- Round 1: $\varepsilon/2$-LDP
- Round 2: $\varepsilon/2$-LDP
- **Total: $\varepsilon$-LDP** ✓

### Why Fresh Randomness Matters
Each round uses **independent** coin flips. No correlation attacks possible!

---

# Slide 33: Privacy Proof - Full Statement

## Formal Theorem

**Theorem**: VA-Edge-LDP satisfies $\varepsilon$-Local Differential Privacy for each private edge.

**Proof**:
For any private edge $e$ and graphs $G, G'$ differing only in $e$:

1. Edge $e$ is queried at most twice (Round 1, Round 2)
2. Each query uses $\varepsilon/2$-LDP Randomized Response
3. By sequential composition: total $\leq \varepsilon$

$$\frac{\Pr[\mathcal{M}(G) \in S]}{\Pr[\mathcal{M}(G') \in S]} \leq e^{\varepsilon/2} \cdot e^{\varepsilon/2} = e^\varepsilon$$

**Public edges**: No privacy claim (by design) ∎

---

# Slide 34: Data Leakage Prevention

## How We Prevent Information Leakage

| Attack Vector | Prevention |
|--------------|------------|
| Which edges exist? | Query ALL possible edges |
| Correlate rounds? | Fresh independent randomness |
| Read raw values? | Only noisy bits transmitted |
| Timing attacks? | Same protocol for all edges |
| Infer from queries? | Every edge position queried |

### The Aggregator NEVER Sees:
- ✗ True edge existence for private edges
- ✗ Which reports are truthful
- ✗ Original graph structure

---

# Slide 35: Experimental Setup

## Evaluation Configuration

### Dataset
- **Facebook Social Network** (SNAP)
- 4,039 nodes, 88,234 edges
- Power-law degree distribution (α ≈ 2.5)

### Parameters
- Privacy: ε ∈ {0.5, 1.0, 2.0, 4.0}
- Public fraction: ~50%
- Trials: 5 per configuration

### Metrics
- Mean Absolute Error (MAE)
- Relative Error (%)
- Improvement over Uniform LDP

---

# Slide 36: Results - Triangle Count

## VA-Edge-LDP vs Uniform Edge-LDP

| ε | Uniform Error | VA-LDP Error | Improvement |
|---|--------------|--------------|-------------|
| 0.5 | 77.5% | 38.4% | **+50%** |
| 1.0 | 71.8% | 17.6% | **+76%** |
| 2.0 | 58.2% | 4.8% | **+92%** |
| 4.0 | 31.2% | 1.3% | **+96%** |

### Key Finding
VA-Edge-LDP achieves up to **96% improvement** in triangle counting accuracy!

---

# Slide 37: Results - All Metrics

## Comprehensive Comparison

| Metric | Best Improvement | At ε |
|--------|-----------------|------|
| Triangles | +96% | 4.0 |
| 3-Stars | +87% | 4.0 |
| 2-Stars | +88% | 4.0 |
| Max Degree | +46% | 2.0 |
| Edge Count | +54% | 1.0 |

### Overall
**Average improvement: 31.6%** across all metrics and privacy levels!

---

# Slide 38: Why VA-Edge-LDP Wins

## The Source of Improvement

### 1. Zero Noise on Public Edges
```
Public edges contribute EXACT values
No variance, no bias correction needed
```

### 2. Lower IPW Weights
```
Mixed triangles (some public, some private):
- Lower detection probability needed
- Lower IPW weights
- Lower variance
```

### 3. Compound Effect
```
With 50% public edges:
- 12.5% triangles: weight = 1 (exact!)
- 37.5% triangles: weight ≈ 2
- 37.5% triangles: weight ≈ 4  
- 12.5% triangles: weight ≈ 7

vs Uniform: ALL triangles weight ≈ 7
```

---

# Slide 39: Limitations & Future Work

## Current Limitations

1. **O(n²) Complexity**: Must query all possible edges
2. **Visibility Must Be Public**: Can't hide which edges are public
3. **Two-Round Communication**: Requires interaction

## Future Directions

1. **Sampling**: Reduce to O(m) for sparse graphs
2. **Double Clipping**: Further variance reduction
3. **Shuffle Model**: Even better utility with shuffler
4. **More Statistics**: Clustering coefficient, centrality

---

# Slide 40: Conclusion

## Summary

### What We Built
- **VA-Edge-LDP**: First visibility-aware Edge-LDP framework
- **Four Algorithms**: Edge count, triangles, k-stars, max degree
- **Formal Guarantees**: ε-LDP for all private edges

### Key Innovations
1. Leverage public edges for exact reporting
2. Two-round protocol with IPW for unbiased estimation
3. Proven privacy with prevented data leakage

### Results
- Up to **96% improvement** over Uniform Edge-LDP
- **31.6% average improvement** across all metrics
- **Same privacy guarantee**, better utility!

---

# Slide 41: References

## Key Papers

1. **Warner (1965)**: Randomized Response - original technique

2. **Duchi, Jordan, Wainwright (2013)**: Local Privacy Minimax Rates

3. **Imola, Murakami, Chaudhuri (2021)**: Locally Differentially Private Analysis of Graph Statistics - USENIX Security

4. **Qin et al. (2017)**: Heavy Hitter Estimation under LDP

5. **Ye & Barg (2018)**: Optimal schemes for discrete distribution estimation under LDP

---

# Slide 42: Thank You

## Questions?

### Code Available
```
visibility_aware_edge_ldp/
├── true_ldp.py      # Core LDP algorithms
├── uniform_ldp.py   # Baseline comparison
├── compare_ldp.py   # Evaluation script
├── model.py         # Visibility-aware graph model
└── ALGORITHMS.md    # Detailed documentation
```

### Contact
[Your contact information]

---

# Appendix A: Randomized Response Probabilities

## Quick Reference

| ε | p (truth prob) | q (flip prob) | p² (two-round) |
|---|----------------|---------------|----------------|
| 0.5 | 0.62 | 0.38 | 0.38 |
| 1.0 | 0.73 | 0.27 | 0.53 |
| 2.0 | 0.88 | 0.12 | 0.77 |
| 4.0 | 0.98 | 0.02 | 0.96 |

Higher ε → More accuracy, less privacy

---

# Appendix B: IPW Weight Table

## Triangle IPW Weights by Edge Composition

| Public Edges | Private Edges | Detection Prob (ε=1) | IPW Weight |
|--------------|---------------|---------------------|------------|
| 3 | 0 | 1.000 | 1.0 |
| 2 | 1 | 0.533 | 1.9 |
| 1 | 2 | 0.284 | 3.5 |
| 0 | 3 | 0.151 | 6.6 |

---

# Appendix C: Complexity Analysis

## Computational Costs

| Algorithm | Time | Space |
|-----------|------|-------|
| Edge Count | O(n²) | O(n²) |
| Triangle Count | O(n³) worst | O(n²) |
| K-Star Count | O(n² · k) | O(n²) |
| Max Degree | O(n²) | O(n²) |

**Bottleneck**: Querying all possible edges

**Optimization opportunity**: Sampling for large graphs

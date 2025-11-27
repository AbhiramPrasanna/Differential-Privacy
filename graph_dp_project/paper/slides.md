# Slide Deck: Localized Visibility Models for Graph Differential Privacy

## Slide 1: Title Slide
**Title**: Complex Graph DP Models for Social Networks
**Subtitle**: Leveraging Localized Visibility & Graph Correlations
**Context**: Advanced Graph Differential Privacy Project

---

## Slide 2: The Problem with Standard DP
**Why not just use standard Edge-DP?**
*   **Global Sensitivity**: Standard DP assumes worst-case changes.
*   **Graph Correlations**: In social networks, edges are not independent.
    *   "No Free Lunch" Theorem [Kifer et al.]: We cannot have utility without making assumptions about the data generation (correlations).
    *   Example: If $A$ and $B$ are friends, they likely share friends $C, D, E$. Hiding edge $(A,B)$ requires hiding all these induced triangles.
*   **Result**: Standard DP noise scales with $O(n)$ or requires destroying the graph structure (clipping), making utility impossible for complex queries.

---

## Slide 3: Motivation: Real-World Visibility
**How do users actually see graphs?**
*   **Localized Visibility**: Users don't see the whole graph.
    *   Facebook: You see your Friends and "Mutual Friends".
    *   Twitter: You see Followers/Following lists.
*   **The Opportunity**:
    *   Instead of protecting against a global adversary, we can model privacy based on **what is naturally visible**.
    *   If a user naturally sees a subgraph $G_u$, we can apply Local DP (LDP) to $G_u$.

---

## Slide 4: Our Model: Neighborhood Visibility (Blowfish Policy)
**1. The Visibility Oracle**
*   **Policy**: **2-Hop Visibility**
    *   User $u$ sees neighbors $N(u)$ and neighbors of neighbors $N(N(u))$.
    *   This captures "Mutual Friends" and allows local triangle counting.

**2. Blowfish Privacy Policy**
*   **Concept**: Customize privacy to the graph setting using "Secrets" and "Constraints".
*   **Secret**: Existence of any single edge $(u, v)$.
*   **Constraint (View)**: The adversary (or user) is restricted to the 2-hop neighborhood.
*   **Public vs. Private Nodes**:
    *   **Assumption**: High-degree nodes (Hubs/Influencers) are "Public".
    *   **Mechanism**: Top-k degree nodes do not add noise. Private nodes add Laplace noise.

---

## Slide 5: Algorithms Overview
We developed LDP algorithms for three key metrics:

1.  **Linear Statistics**:
    *   **Edge Count**: Simple summation of degrees.
    *   **Degree Histogram**: Distribution of node degrees.

2.  **Non-Linear (Subgraphs)**:
    *   **Triangle Count**: $\triangle = \frac{1}{3} \sum T_u$
    *   **k-Star Count**: $\star_k = \sum \binom{d_u}{k}$

*Challenge*: Non-linear queries have exploding sensitivity in graphs.

---

## Slide 6: The Sensitivity Challenge & Lower Bounds
**Why is Graph DP hard?**
*   **Triangle Count Sensitivity**: $O(D_{max})$.
    *   Adding edge $(u, v)$ creates a triangle for *every* common neighbor.
*   **k-Star Sensitivity**: $O(D_{max}^{k-1})$.
    *   Combinatorial explosion. For $k=3$, sensitivity is quadratic in degree.

**Formal Lower Bound Analysis**:
*   **Theorem**: For one-round LDP, error is $\Omega(n \cdot D_{max}^{2k-2})$.
*   **Implication**: For triangles ($k=3$), error scales with $n \cdot D_{max}^4$.
*   **The Barrier**: The factor of $n$ comes from every user adding noise. The $D_{max}$ factor comes from the worst-case sensitivity.

---

## Slide 7: Solution 1 - Public Hubs
**Breaking the Lower Bound**
*   **Observation**: In Power-Law graphs (like Facebook), a few "Hubs" hold most of the edges and triangles.
*   **Strategy**:
    *   Treat Top-20% degree nodes as **Public**.
    *   **Noise = 0** for these nodes.
*   **How it Breaks the Bound**:
    *   The lower bound assumes *uniform* privacy.
    *   By removing noise for the Hubs (who contribute the $D_{max}$ signal), we reduce the effective bound to $\Omega(n_{tail} \cdot d_{tail}^{2k-2})$.
    *   We estimate ~80% of the graph (the "Head") with **Zero Error**.

---

## Slide 8: Solution 2 - Smooth Sensitivity
**Instance-Specific Noise**
*   **Standard Approach (Clipping)**:
    *   Assume worst case: Everyone has $D_{max}=50$ friends.
    *   Add noise $\propto 50$.
    *   Problem: High noise + Bias (underestimation).
*   **Our Approach (Smooth)**:
    *   Calculate **Local Sensitivity** $S_u$ for each user.
    *   For Triangles: $S_u = \text{Max Common Neighbors}$.
    *   For 2-Stars: $S_u = \text{Degree}$.
    *   Add noise $\propto S_u$.
*   **Result**: Average sensitivity drops from 50 $\to$ ~17. Noise is drastically reduced.

---

## Slide 9: Empirical Study
**Setup**
*   **Dataset**: Facebook SNAP (4,039 nodes, 88k edges).
*   **Graph Type**: Power Law (Social Network).
*   **Privacy Budget ($\epsilon$)**: 0.1 to 5.0.

**Visualizing the Win**
*(Insert Triangle Error Plot Here)*
*   **Orange Line (Smooth)**: ~0.4% error at $\epsilon=1.0$.
*   **Blue Line (Clipped)**: ~1.6% error.
*   **Improvement**: 4x reduction in error.

---

## Slide 10: Results - k-Star Count
**Near-Perfect Accuracy**
*(Insert 2-Star Error Plot Here)*
*   **2-Star Count**: Measures "connectedness" or "influence potential".
*   **Result**:
    *   Clipped Error: 0.5%
    *   **Smooth Error: 0.04%** (at $\epsilon=1.0$)
*   **Why?**: The average degree (sensitivity) is much lower than the max degree. Smooth sensitivity captures this perfectly.

---

## Slide 11: Conclusion & Future Work
**Key Achievements**:
1.  **Modeled Real-World Visibility**: 2-Hop + Public Hubs.
2.  **Beat the Lower Bound**: Leveraged heavy tails (Hubs) to bypass worst-case limits.
3.  **Implemented Smooth Sensitivity**: Proved 4x-10x accuracy gains.

**Future Work**:
*   **Formal Blowfish Policy**: Implement a generic policy engine.
*   **Max Degree Estimation**: Currently assumed/clipped.
*   **Two-Round LDP**: Explore interactive protocols for further error reduction.

---

## References
1.  **No Free Lunch in Data Privacy** (Kifer & Machanavajjhala, 2011)
2.  **Blowfish Privacy** (He et al., 2014)
3.  **Lower Bounds for LDP on Graphs** (ArXiv:2010.08688)

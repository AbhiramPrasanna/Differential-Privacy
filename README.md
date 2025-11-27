# Theoretical Analysis: Bounds & Algorithms

This document provides a comprehensive mathematical analysis of the lower bounds for Graph Local Differential Privacy (LDP) and demonstrates how our **Public Hubs** model bypasses these limitations.

## 1. The Fundamental Lower Bound (The "Impossibility" Result)

For one-round LDP protocols, there exists a fundamental limit on the accuracy of subgraph counting queries.

### 1.1 Theorem Statement

Let $f_k(G)$ be the count of $k$-stars in graph $G$. For any $\epsilon$-LDP mechanism $\mathcal{M}$, the expected squared error (variance) is lower bounded by:

$$
\text{Error}_{LDP} = \mathbb{E}[(\mathcal{M}(G) - f_k(G))^2] = \Omega\left(n \cdot \frac{d_{max}^{2k-2}}{\epsilon^2}\right)
$$

**Variables:**
*   $n$: Number of nodes (users) in the graph.
*   $d_{max}$: The maximum degree in the graph (Global Sensitivity parameter).
*   $k$: The size of the subgraph ($k=2$ for edges, $k=3$ for triangles/2-stars).

### 1.2 Why this is Critical

The term $d_{max}^{2k-2}$ is the dominant factor.

*   **For Triangles ($k=3$)**: The error scales with $d_{max}^4$.
*   **Example**: In a social network with $d_{max} = 1000$:
    *   $d_{max}^4 = 10^{12}$ (1 Trillion).
    *   This noise magnitude often exceeds the actual count, making the result useless.

---

## 2. Our Algorithm: The "Public Hubs" Derivation

Our algorithm does not treat all nodes as "Private". We designate a set of high-degree nodes $V_{pub}$ as **Public** (adding 0 noise) and the rest $V_{priv}$ as **Private**.

### 2.1 The Estimator

The global estimator $\hat{f}$ is the sum of local reports:

$$
\hat{f} = \sum_{u \in V_{pub}} f_u(G) + \sum_{v \in V_{priv}} (f_v(G) + \eta_v)
$$

where $\eta_v \sim \text{Laplace}(S_v / \epsilon)$.

### 2.2 Variance Analysis (Exact Formula)

Since the noise is independent for each user, the total variance is the sum of individual variances. Public nodes contribute 0 variance.

$$
\text{Var}(\hat{f}) = \sum_{v \in V_{priv}} \text{Var}(\eta_v) = \sum_{v \in V_{priv}} 2 \cdot \left(\frac{S_v}{\epsilon}\right)^2
$$

**Key Insight**: The sum is **only** over $V_{priv}$.

### 2.3 Sensitivity $S_v$

For counting $k$-stars, the local sensitivity $S_v$ for user $v$ is:

$$
S_v = \binom{d_v}{k-1}
$$

Substituting this into the variance formula:

$$
\text{Var}_{Ours} = \frac{2}{\epsilon^2} \sum_{v \in V_{priv}} \left( \binom{d_v}{k-1} \right)^2
$$

---

## 3. Comparative Analysis: Why We Win

Let's compare the error scaling of the Standard approach vs. Our approach.

### 3.1 Standard LDP Error

In standard LDP, every node adds noise proportional to the *global* worst case ($d_{max}$).

$$
\text{Error}_{Standard} \approx \frac{n}{\epsilon^2} \cdot \left( \binom{d_{max}}{k-1} \right)^2 \approx \frac{n \cdot d_{max}^{2k-2}}{\epsilon^2}
$$

### 3.2 Public Hubs Error

In our model, we remove the top nodes. Let $d_{tail}$ be the maximum degree among the *Private* nodes ($V_{priv}$).

$$
\text{Error}_{Ours} \approx \frac{n_{priv}}{\epsilon^2} \cdot \left( \binom{d_{tail}}{k-1} \right)^2 \approx \frac{n \cdot d_{tail}^{2k-2}}{\epsilon^2}
$$

### 3.3 The Magnitude of Improvement

In Power Law graphs (like social networks), the degree distribution is heavy-tailed.

*   $d_{max}$ might be 5000 (a celebrity).
*   $d_{tail}$ (after removing top 1% hubs) might be only 50.

**For Triangles ($k=3$):**

*   **Standard Factor**: $5000^4 = 6.25 \times 10^{14}$
*   **Ours Factor**: $50^4 = 6.25 \times 10^6$

**Improvement Factor**:

$$
\frac{\text{Error}_{Standard}}{\text{Error}_{Ours}} \approx \left( \frac{d_{max}}{d_{tail}} \right)^{2k-2} = \left( \frac{5000}{50} \right)^4 = 100^4 = 100,000,000
$$

**Conclusion**: By simply treating the top 1% of nodes as public, we reduce the variance by a factor of **100 million** in this example. This turns an impossible problem into a solvable one.

---

## 4. Summary of Formulas

| Metric | Standard LDP Variance (Bound) | Our Model Variance (Exact) |
| :--- | :--- | :--- |
| **Edge Count** ($k=2$) | $O(n \cdot 1)$ | $O(n_{priv} \cdot 1)$ |
| **2-Stars** ($k=3$) | $O(n \cdot d_{max}^2)$ | $\frac{2}{\epsilon^2} \sum_{v \in V_{priv}} d_v^2$ |
| **Triangles** ($k=3$) | $O(n \cdot d_{max}^2)$ | $\frac{2}{\epsilon^2} \sum_{v \in V_{priv}} S_{tri}(v)^2$ |

*Note: For triangles, our algorithm uses "Smooth Sensitivity" where $S_{tri}(v)$ is the max common neighbors, which is strictly less than or equal to $d_v$.*

---

## 5. Deep Dive: Rigorous Derivation for Power-Law Graphs

To understand the *exact* magnitude of improvement, we must model the graph's degree distribution. Social networks typically follow a **Power Law** distribution:

$$
P(d) \propto d^{-\alpha}
$$

where $\alpha$ is typically between $2$ and $3$.

### 5.1 The Variance Integral

The total variance of our estimator is proportional to the sum of squared sensitivities (which depend on degree $d$). For a continuous approximation, we can integrate over the degree distribution.

Let $N$ be the total nodes, $d_{min}$ be the minimum degree, and $d_{max}$ be the maximum degree (cutoff).

The expected sum of squared degrees (related to 2-star variance) is:

$$
\Sigma_{sq} \approx N \int_{d_{min}}^{d_{max}} d^2 \cdot P(d) \, \mathrm{d}d
$$

Substituting $P(d) = C \cdot d^{-\alpha}$:

$$
\Sigma_{sq} \approx N \cdot C \int_{d_{min}}^{d_{max}} d^{2-\alpha} \, \mathrm{d}d
$$

### 5.2 Case Study: $\alpha = 2.5$

For many social networks, $\alpha \approx 2.5$. The integral becomes $\int d^{-0.5} \, \mathrm{d}d = [2d^{0.5}]$.

#### Standard LDP (Full Integration)

Integration range: $[d_{min}, d_{max}]$.

$$
\text{Var}_{Standard} \propto \sqrt{d_{max}} - \sqrt{d_{min}} \approx \sqrt{d_{max}}
$$

Actually, for Standard LDP, the noise is set by the *worst case* $d_{max}$ for *everyone*.

$$
\text{Total Var}_{Standard} = N \cdot (d_{max})^2
$$

This is the baseline we are fighting.

#### Our Model (Truncated Integration)

In our model, the "Private" nodes are only those with degree $d < d_{cutoff}$ (where $d_{cutoff}$ is the degree of the smallest Public Hub). The noise added by a private node $u$ is proportional to its *actual* degree $d_u$ (Smooth Sensitivity), not $d_{max}$. So we integrate the *actual* squared degrees up to $d_{cutoff}$.

$$
\text{Total Var}_{Ours} \approx N \int_{d_{min}}^{d_{cutoff}} d^2 \cdot d^{-2.5} \, \mathrm{d}d \propto \sqrt{d_{cutoff}}
$$

### 5.3 The Improvement Ratio

Comparing the two variances:

$$
\frac{\text{Var}_{Standard}}{\text{Var}_{Ours}} \approx \frac{N \cdot d_{max}^2}{N \cdot \sqrt{d_{cutoff}}} = \frac{d_{max}^2}{\sqrt{d_{cutoff}}}
$$

**Numerical Example**:

*   $N = 1,000,000$
*   $d_{max} = 10,000$ (Celebrity)
*   We make top 1% public $\rightarrow d_{cutoff} \approx 100$ (Ordinary user)

**Standard Variance**: Proportional to $10,000^2 = 100,000,000$.

**Our Variance**: Proportional to $\sqrt{100} = 10$.

**Improvement Factor**:

$$
\frac{100,000,000}{10} = 10,000,000 \times
$$

### 5.4 Conclusion on Bounds

Our algorithm changes the error bound dependency from the **Maximum Degree** ($d_{max}$) to the **Cutoff Degree** ($d_{cutoff}$) of the private tail.

*   **Standard Bound**: $\Omega(n \cdot d_{max}^{2k-2})$
*   **Our Bound**: $O(n \cdot d_{cutoff}^{2k-2})$

Since $d_{cutoff} \ll d_{max}$ in power-law graphs, this represents a massive theoretical and practical improvement.

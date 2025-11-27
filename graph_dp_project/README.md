# Localized Visibility Models for Graph Differential Privacy

## Overview
This project implements and evaluates a **Localized Differential Privacy (LDP)** model for social networks. It addresses the challenge of high sensitivity in graph data by leveraging natural visibility scopes (2-hop neighborhoods) and a hybrid **Public/Private Node** model.

The core innovation is the **"Public Hubs" strategy**: treating high-degree nodes (hubs) as public, which allows for accurate estimation of complex subgraph statistics (like triangles and k-stars) that are otherwise impossible under standard LDP lower bounds.

## Key Features
*   **2-Hop Visibility Model**: Users see their neighbors and their neighbors' neighbors.
*   **Public/Private Distinction**: Top-k degree nodes are treated as Public (no noise), while others are Private (LDP noise).
*   **Algorithms**:
    *   **Edge Count** (Sensitivity 1)
    *   **Triangle Count** (Sensitivity $D_{max}$)
    *   **k-Star Count** (Sensitivity $\binom{D_{max}-1}{k-1}$)
*   **Evaluation**: Empirical study on the **Facebook SNAP** dataset (Power Law distribution).

## Setup & Installation

1.  **Prerequisites**: Python 3.8+
2.  **Dependencies**:
    ```bash
    pip install networkx numpy pandas matplotlib scipy
    ```
    *(Note: The project includes a local `libs` directory setup if needed)*

## Usage

1.  **Download Data**:
    The project uses the Facebook SNAP dataset. Run the downloader script:
    ```bash
    python src/download_data.py
    ```

2.  **Run Experiments**:
    Execute the main experiment script to run the evaluation:
    ```bash
    python src/experiment.py
    ```
    This will:
    *   Load the Facebook graph.
    *   Sample a power-law subgraph.
    *   Run DP algorithms for $\epsilon \in [0.1, 5.0]$.
    *   Save results to `paper/results_comprehensive.csv`.

## Results Summary
Our evaluation on the Facebook graph demonstrates high utility even at low epsilon ($\epsilon=1.0$):

| Metric | Relative Error ($\epsilon=1.0$) |
|--------|---------------------------------|
| Edge Count | ~0.2% |
| Triangle Count | ~0.6% |
| 2-Star Count | ~1.5% |

**Why it works**: The "Public Hubs" strategy effectively bypasses the $\Omega(n)$ lower bound for LDP by removing noise from the nodes that contribute the most to the signal (the hubs).

## Project Structure
*   `src/`: Source code for model, algorithms, and experiments.
*   `data/`: Directory for dataset storage.
*   `paper/`: Contains the research paper (`paper.md`) and result files.

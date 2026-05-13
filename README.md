# MRWP Workplan: Fragmentation in Signed Social Networks

**Team Members:** Kaj Geijsberts, Romane Gourlet, Samu Herczeg, Emilien Pelosse

---

## 1. Topic, Context, and Knowledge Gap
Various online platforms exhibit rich signed-like dynamics, where users label relationships as positive (trust) or negative (distrust). Understanding when and why communities in these networks fragment has direct implications for moderation policy and the spread of polarization. 

While signed networks are common, most community detection algorithms focus primarily on positive edges. As Esmailian & Jalili (2015) note, community detection in signed networks has been “significantly underexplored” compared to unsigned ones. Research suggests that negative edges are not symmetric in their effects and can meaningfully alter detected community structures. Even when negative edges do not change a partition, they may still carry information about community stability. We aim to directly test whether the proportion of negative ties within a community predicts its robustness using the WikiElec and Epinions datasets.

## 2. Initial Research Question
* Does accounting for negative edges reveal fragmentation patterns that would otherwise have been missed by treating all edges as positive?
* Does accounting for negative edges reveal fragmentation patterns that would otherwise have been missed by only treating positive edges?

## 3. Data
We will utilize the following datasets from the [SNAP Database](https://snap.stanford.edu/data/#signnets):
* **WikiElec:** Contains Wikipedia Requests for Adminship (RfA). Votes are coded as +1 (support), 0 (neutral), and -1 (oppose). The dataset includes ~2,800 elections, 100,000 votes, and 7,000 users.
* **Epinions:** A consumer review platform where users mark others as trusted or distrusted. This will be used as a reference point for comparison with synthetic models.

## 4. Methodology (Python / NetworkX)

### Structural Balance Theory
We utilize the base properties of structural balance theory, which classifies triangles as:
* **Balanced:** Product of edge signs is positive (e.g., friend of a friend is a friend).
* **Unbalanced:** Product of edge signs is negative.

### Handling Directed Edges
As balance theory assumes undirected edges, we symmetrize directed edges using these rules:
1. **Mutual Agreement:** If A→B and B→A have the same sign, keep that sign.
2. **One-sided Edge:** If only A→B exists, we infer the sign from common neighbors. If they relate to shared neighbors similarly, the edge is positive; if oppositely, negative. Default to the explicit sign if no common neighbors exist.
3. **Conflicting Edges:** If A trusts B but B distrusts A, the edge is treated as negative (distrust dominates).

### Community Detection Approach
* **Louvain (Unsigned Baseline):** Standard method in the literature, used here to ignore signs for the baseline.
* **CPMap (Sign-aware Method):** Models network structure via a random walk where negative edges act as barriers. This allows us to see if accounting for negative edges produces structurally different communities.

## 5. Planned Experiments

### Experiment 1: Balance Profiling
Run community detection ignoring edge signs to obtain an initial partition. For each community, compute a **balance score** (fraction of internal triangles that are balanced). This creates a "tension map" to quantify internal stability.

### Experiment 2: Detection Sensitivity
Run detection twice: once ignoring signs and once weighting edges with their sign value (negative weights for distrust). Compare partitions to assess if including signs produces meaningfully different structures.

### Experiment 3: Fragmentation Test
Rank communities from Experiment 1 by balance score. Examine whether communities with low balance scores (high tension) tend to split into smaller communities when sign-aware detection (CPMap) is applied.

### Experiment 4: Synthetic Robustness Check (Barabási–Albert Model)
Generate synthetic networks using the Barabási–Albert model with varying proportions of negative edges (10% to 90%). Observe at what point communities fragment as distrust increases to create a baseline for real-world data.

## 6. Limitations
* **Dataset Age:** WikiElec and Epinions are older datasets and may not reflect modern signed dynamics.
* **Sparsity:** Negative edges represent a minority of the total edges in these datasets.
* **Scope:** The initial research question is complex and may be refined as experiments progress.

## 7. References
* Blondel, V. D., Guillaume, J.-L., Lambiotte, R., & Lefebvre, E. (2008). Fast unfolding of communities in large networks. *Journal of Statistical Mechanics: Theory and Experiment*.
* Diaz-Diaz, F., et al. (2025). Signed networks: Theory, methods, and applications. *arXiv preprint*.
* Esmailian, P., & Jalili, M. (2015). Community detection in signed networks: the role of negative ties in different scales. *Scientific Reports*.
* Mueller, M., & Ramkumar, S. (2023). Signed networks - The role of negative links for the diffusion of innovation. *Technological Forecasting and Social Change*.
* Leskovec, J., Huttenlocher, D., & Kleinberg, J. (2010). Signed networks in social media. *CHI '10*.

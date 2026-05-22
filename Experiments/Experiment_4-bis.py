import networkx as nx
import community as community_louvain
import random
import matplotlib.pyplot as plt
import numpy as np
from itertools import combinations

# ── Signed BA Model ────────────────────────────────────────────────────────

def signed_ba_model(n, m, p_positive=0.7, seed=None):
    """
    Build a Signed Barabási–Albert graph.

    Parameters
    ----------
    n           : total number of nodes
    m           : edges added per new node (keep low, e.g. 2-3)
    p_positive  : probability that a new edge is positive (+1)
    seed        : random seed for reproducibility

    Returns
    -------
    G : nx.Graph with edge attribute 'sign' in {+1, -1}
    """
    if seed is not None:
        random.seed(seed)

    G = nx.Graph()

    # seed clique (m nodes, all edges signed)
    G.add_nodes_from(range(m))
    for i in range(m):
        for j in range(i + 1, m):
            sign = 1 if random.random() < p_positive else -1
            G.add_edge(i, j, sign=sign)

    # preferential attachment
    for new_node in range(m, n):
        G.add_node(new_node)

        degrees = dict(G.degree())
        nodes   = list(degrees.keys())
        weights = [degrees[v] for v in nodes]
        total   = sum(weights)

        targets = set()
        while len(targets) < m:
            r = random.random() * total
            cumulative = 0
            for node, w in zip(nodes, weights):
                cumulative += w
                if r <= cumulative:
                    if node != new_node:
                        targets.add(node)
                    break

        for target in targets:
            sign = 1 if random.random() < p_positive else -1
            G.add_edge(new_node, target, sign=sign)

    return G


# ── Visualise ──────────────────────────────────────────────────────────────

def visualise_signed_network(G, title="Signed Barabási–Albert Network", 
                              save_path="signed_ba.png"):
    pos   = nx.spring_layout(G, seed=42)
    signs = [G[u][v]['sign'] for u, v in G.edges()]

    pos_edges = [(u, v) for (u, v), s in zip(G.edges(), signs) if s ==  1]
    neg_edges = [(u, v) for (u, v), s in zip(G.edges(), signs) if s == -1]

    plt.figure(figsize=(10, 8))
    nx.draw_networkx_nodes(G, pos, node_size=80, node_color='#3498db', alpha=0.85)
    nx.draw_networkx_edges(G, pos, edgelist=pos_edges, edge_color='#2ecc71',
                           width=1.4, alpha=0.7, label='Positive (+1)')
    nx.draw_networkx_edges(G, pos, edgelist=neg_edges, edge_color='#e74c3c',
                           width=1.4, alpha=0.7, style='dashed', label='Negative (−1)')
    plt.legend(loc='upper left')
    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.show()


# ── Balance Score Helpers ──────────────────────────────────────────────────

def get_triangles(G, nodes):
    """Return all triangles within a set of nodes."""
    triangles = []
    node_list = list(nodes)
    for i, j, k in combinations(node_list, 3):
        if G.has_edge(i, j) and G.has_edge(j, k) and G.has_edge(i, k):
            triangles.append((i, j, k))
    return triangles


def balance_score(G, community_nodes):
    """
    Compute the fraction of balanced triangles within a community.
    A triangle is balanced if the product of its edge signs is positive.
    Returns None if no triangles exist.
    """
    triangles = get_triangles(G, community_nodes)
    if not triangles:
        return None

    balanced = sum(
        1 for i, j, k in triangles
        if G[i][j]['sign'] * G[j][k]['sign'] * G[i][k]['sign'] > 0
    )
    return balanced / len(triangles)


# ── Experiment 1: Balance Profiling ───────────────────────────────────────

def experiment_1(G):
    """
    1. Run Louvain community detection (ignoring signs)
    2. Compute balance score for each detected community
    3. Visualise the distribution of balance scores
    """

    # Step 1 — run Louvain on unsigned graph
    partition = community_louvain.best_partition(G)

    # Step 2 — group nodes by community
    communities = {}
    for node, comm_id in partition.items():
        communities.setdefault(comm_id, set()).add(node)

    print(f"Number of communities detected: {len(communities)}")

    # Step 3 — compute balance score per community
    scores = {}
    for comm_id, nodes in communities.items():
        score = balance_score(G, nodes)
        scores[comm_id] = score
        if score is not None:
            print(f"  Community {comm_id}: {len(nodes)} nodes, "
                  f"balance score = {score:.3f}")
        else:
            print(f"  Community {comm_id}: {len(nodes)} nodes, no triangles")

    # Step 4 — filter out communities with no triangles
    valid_scores = [s for s in scores.values() if s is not None]
    print(f"\nCommunities with triangles: {len(valid_scores)} / {len(communities)}")
    print(f"Mean balance score: {np.mean(valid_scores):.3f}")
    print(f"Min balance score:  {np.min(valid_scores):.3f}")
    print(f"Max balance score:  {np.max(valid_scores):.3f}")

    # Step 5 — visualise distribution
    plt.figure(figsize=(8, 5))
    plt.hist(valid_scores, bins=20, color='#3498db', 
             edgecolor='white', alpha=0.85)
    plt.axvline(np.mean(valid_scores), color='#e74c3c', linestyle='--',
                label=f'Mean = {np.mean(valid_scores):.3f}')
    plt.xlabel("Balance Score")
    plt.ylabel("Number of Communities")
    plt.title("Distribution of Balance Scores per Community (Experiment 1)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("experiment_1_balance_scores.png", dpi=150)

    return partition, communities, scores


# ── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # build network
    G = signed_ba_model(n=1000, m=3, p_positive=0.7, seed=42)

    # visualise
    visualise_signed_network(G)

    # run experiment 1
    partition, communities, scores = experiment_1(G)
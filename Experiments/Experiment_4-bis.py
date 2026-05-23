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



if __name__ == "__main__":
    # build network
    G = signed_ba_model(n=7000, m=3, p_positive=0.5, seed=42)
    #G1 = signed_ba_model(n=7000, m = 3, p_positive=0.1, seed=42)
    #G2 = signed_ba_model(n=7000, m = 3, p_positive=0.9, seed=42)
    # visualise
    visualise_signed_network(G)
    #visualise_signed_network(G1, save_path="signed_ba1.png")
    #visualise_signed_network(G2, save_path="signed_ba2.png")

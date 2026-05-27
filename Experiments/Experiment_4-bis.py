import networkx as nx
import community as community_louvain
import random
import matplotlib.pyplot as plt
import numpy as np
from itertools import combinations
import pickle 
import pandas as pd

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
    # matching density of WikiElec network, which is quite big but mostly has a very high m
    # in Wiki_data_info.py, we find that the WikiElec neetwork density is 0.00398, so about 0.004
    # density = 2m/n -> m = density *n /2 = 0-004 * 1000/2 = 2
    G = signed_ba_model(n=1000, m=2, p_positive=0.5, seed=42)
    with open("signed_ba.pkl", "wb") as f:
        pickle.dump(G, f)
    G1 = signed_ba_model(n=1000, m=2, p_positive=0.1, seed=42)
    with open("signed_ba1.pkl", "wb") as f:
        pickle.dump(G1, f)
    G2 = signed_ba_model(n=1000, m=2, p_positive=0.9, seed=42)
    with open("signed_ba2.pkl", "wb") as f:
        pickle.dump(G2, f)
    # visualise
    visualise_signed_network(G)
    visualise_signed_network(G1, save_path="signed_ba1.png")
    visualise_signed_network(G2, save_path="signed_ba2.png")

    #but if we want to move away from the wikiElec network to oserve BA model as a controlled synthetic test :
    G3 = signed_ba_model(n=1000, m=4, p_positive=0.5, seed=42)
    with open("signed_ba3.pkl", "wb") as f:
        pickle.dump(G, f)

    # save csv from the fresh graph
    edges = [(u, v, d['sign']) for u, v, d in G.edges(data=True)]
    df = pd.DataFrame(edges, columns=['node_A', 'node_B', 'sign'])
    df.to_csv("signed_ba3.csv", index=False)

    print(f"PKL edges: {G.number_of_edges()}")
    print(f"CSV rows:  {len(df)}")

    G4 = signed_ba_model(n=1000, m=4, p_positive=0.1, seed=42)
    with open("signed_ba4.pkl", "wb") as f:
        pickle.dump(G4, f)
    G5 = signed_ba_model(n=1000, m=4, p_positive=0.9, seed=42)
    with open("signed_ba5.pkl", "wb") as f:
        pickle.dump(G5, f)


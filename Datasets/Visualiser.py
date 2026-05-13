import gzip
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Load a sample of the graph
G = nx.DiGraph()

with gzip.open('soc-sign-epinions.gz', 'rt') as f:
    for line in f:
        if line.startswith('#'):
            continue
        parts = line.strip().split()
        u, v, sign = int(parts[0]), int(parts[1]), int(parts[2])
        G.add_edge(u, v, sign=sign)
        if G.number_of_edges() >= 500:  # sample size, increase if you want
            break

# Layout
pos = nx.spring_layout(G, seed=42)

# Separate edges by sign
positive_edges = [(u, v) for u, v, d in G.edges(data=True) if d['sign'] == 1]
negative_edges = [(u, v) for u, v, d in G.edges(data=True) if d['sign'] == -1]

# Draw
plt.figure(figsize=(12, 8))

nx.draw_networkx_nodes(G, pos, node_size=30, node_color='steelblue', alpha=0.8)
nx.draw_networkx_edges(G, pos, edgelist=positive_edges, edge_color='green', alpha=0.5, arrows=True, width=0.8)
nx.draw_networkx_edges(G, pos, edgelist=negative_edges, edge_color='red', alpha=0.5, arrows=True, width=0.8)

# Legend
legend = [
    mpatches.Patch(color='green', label='Trust (+1)'),
    mpatches.Patch(color='red', label='Distrust (-1)')
]
plt.legend(handles=legend, fontsize=11)
plt.title('Epinions Signed Social Network (sample)', fontsize=14)
plt.axis('off')
plt.tight_layout()
plt.savefig('graph.png', dpi=150)
plt.show()
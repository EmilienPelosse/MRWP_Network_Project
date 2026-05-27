import pandas as pd
import networkx as nx

# ── Load Epinions ─────────────────────────────────────────────────────────────
# Format: tab-separated, header lines start with #
# Columns: FromNodeId  ToNodeId  Sign
df = pd.read_csv(
    'soc-sign-epinions.txt',
    sep='\t',
    comment='#',
    header=None,
    names=['source', 'target', 'sign']
)

# Remove self-loops (e.g. node 5 → 5 in the raw data)
df = df[df['source'] != df['target']]

# Remove neutral edges if any (sign = 0)
df = df[df['sign'] != 0]

# Aggregate duplicate edges between the same nodes using majority rule
df = df.groupby(['source', 'target'])['sign'].agg(
    lambda x: 1 if x.sum() > 0 else -1
).reset_index()

# ── Build directed graph ──────────────────────────────────────────────────────
G = nx.DiGraph()
for _, row in df.iterrows():
    G.add_edge(row['source'], row['target'], sign=row['sign'])

print(f"Directed graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
print(f"Positive edges: {sum(1 for _, _, d in G.edges(data=True) if d['sign'] ==  1)}")
print(f"Negative edges: {sum(1 for _, _, d in G.edges(data=True) if d['sign'] == -1)}")
print("\nSample directed edges:")
print(df.head())

# ── Symmetrize ────────────────────────────────────────────────────────────────
def symmetrize(G):
    """
    Symmetrize a directed signed graph into an undirected signed graph.

    Rules:
    1. Mutual agreement  (A→B and B→A same sign)      → keep that sign
    2. Conflicting       (A→B and B→A different sign)  → distrust dominates → -1
    3. One-sided         (A→B, no B→A)                 → use explicit edge sign directly
    """
    U = nx.Graph()
    visited = set()

    for u, v, data in G.edges(data=True):
        if (u, v) in visited or (v, u) in visited:
            continue
        visited.add((u, v))

        sign_uv = data['sign']

        if G.has_edge(v, u):
            sign_vu = G[v][u]['sign']
            if sign_uv == sign_vu:
                U.add_edge(u, v, sign=sign_uv)   # mutual agreement
            else:
                U.add_edge(u, v, sign=-1)         # conflicting → distrust dominates
        else:
            U.add_edge(u, v, sign=sign_uv)        # one-sided → use explicit sign

    return U

U = symmetrize(G)

print(f"\nUndirected graph: {U.number_of_nodes()} nodes, {U.number_of_edges()} edges")
print(f"Positive edges: {sum(1 for _, _, d in U.edges(data=True) if d['sign'] ==  1)}")
print(f"Negative edges: {sum(1 for _, _, d in U.edges(data=True) if d['sign'] == -1)}")

# ── Save outputs (same format as WikiElec) ────────────────────────────────────
df.to_csv('../Experiments/epinions_edges.csv', index=False)

symmetric_edges = [
    {'node_A': u, 'node_B': v, 'sign': data['sign']}
    for u, v, data in U.edges(data=True)
]
df_symmetric = pd.DataFrame(symmetric_edges)
df_symmetric.to_csv('../Experiments/epinions_edges_symmetric.csv', index=False)

print("\nSaved:")
print("  epinions_edges.csv          ← directed aggregated edges")
print("  epinions_edges_symmetric.csv ← undirected symmetric edges (same format as wiki_edges_symmetric.csv)")
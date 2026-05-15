import pandas as pd
import networkx as nx


edges = []

# Read the file and extract edges
with open('wikiElec.ElecBs3.txt', 'r', encoding='latin-1') as f:
    candidate_id = None
    for line in f:
        line = line.strip()
        if line.startswith('U'):
            parts = line.split()
            candidate_id = int(parts[1])
        elif line.startswith('V') and candidate_id is not None:
            parts = line.split()
            vote = int(parts[1])
            voter_id = int(parts[2])
            edges.append((voter_id, candidate_id, vote))

# Create a DataFrame
df = pd.DataFrame(edges, columns=['source', 'target', 'sign'])

# Remove neutral edges (sign = 0)
df = df[df['sign'] != 0]

# Aggregate multiple edges between the same nodes
df = df.groupby(['source', 'target'])['sign'].agg(
    lambda x: 1 if x.sum() > 0 else -1
).reset_index()

# Build the graph
G = nx.DiGraph()
for _, row in df.iterrows():
    G.add_edge(row['source'], row['target'], sign=row['sign'])

print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
print(f"Positive edges: {sum(1 for _, _, d in G.edges(data=True) if d['sign'] == 1)}")
print(f"Negative edges: {sum(1 for _, _, d in G.edges(data=True) if d['sign'] == -1)}")

print("Header of the DataFrame:")
print(df.head())

# Symmetrize the graph

import networkx as nx

def symmetrize(G):
    """
    Symmetrize a directed signed graph into an undirected signed graph.
    
    Rules:
    1. Mutual agreement (A→B and B→A same sign): keep that sign
    2. Conflicting (A→B and B→A different sign): distrust dominates → -1
    3. One-sided (A→B, no B→A): infer from common neighbors
       - Same relation to common neighbors → +1
       - Opposite relation → -1
       - No common neighbors → default to explicit edge sign
    """
    
    U = nx.Graph()  # undirected output graph
    visited = set()

    for u, v, data in G.edges(data=True):
        if (u, v) in visited or (v, u) in visited:
            continue
        visited.add((u, v))

        sign_uv = data['sign']

        # Case 1 & 2: mutual edge exists
        if G.has_edge(v, u):
            sign_vu = G[v][u]['sign']
            if sign_uv == sign_vu:
                U.add_edge(u, v, sign=sign_uv)        # mutual agreement
            else:
                U.add_edge(u, v, sign=-1)             # conflicting → distrust dominates

        # Case 3: one-sided edge
        else:
            common = set(G.successors(u)) & set(G.successors(v))
            
            if not common:
                # No common neighbors → default to explicit sign
                U.add_edge(u, v, sign=sign_uv)
            else:
                # Infer from common neighbors
                scores = []
                for c in common:
                    sign_uc = G[u][c]['sign']
                    sign_vc = G[v][c]['sign']
                    # same relation to c → positive, opposite → negative
                    scores.append(1 if sign_uc == sign_vc else -1)
                
                inferred = 1 if sum(scores) > 0 else -1
                U.add_edge(u, v, sign=inferred)

    return U

# Apply
U = symmetrize(G)

print(f"Undirected graph: {U.number_of_nodes()} nodes, {U.number_of_edges()} edges")
print(f"Positive edges: {sum(1 for _, _, d in U.edges(data=True) if d['sign'] == 1)}")
print(f"Negative edges: {sum(1 for _, _, d in U.edges(data=True) if d['sign'] == -1)}")
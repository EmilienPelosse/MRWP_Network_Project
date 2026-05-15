# Run community detection ignoring edge signs to obtain an initial partition. For each community, compute a balance score (fraction of internal triangles that are balanced). This # creates a "tension map" to quantify internal stability.
import networkx as nx
import community as community_louvain  # pip install python-louvain
import matplotlib.pyplot as plt
import pandas as pd

# ── Load graph ────────────────────────────────────────────────────────────────
df = pd.read_csv('edges.csv')
U = nx.Graph()

for _, row in df.iterrows():
    U.add_edge(row['source'], row['target'], sign=row['sign'])

# ── Step 1: Unsigned Louvain partition ────────────────────────────────────────
# Strip signs — Louvain only sees structure, not sign
U_unsigned = nx.Graph()
U_unsigned.add_edges_from(U.edges())

partition = community_louvain.best_partition(U_unsigned, random_state=42)
# partition = {node_id: community_id, ...}

n_communities = len(set(partition.values()))
print(f"Louvain detected {n_communities} communities")

# ── Step 2: Balance score per community ───────────────────────────────────────
def balance_score(G_signed, nodes):
    """
    Fraction of closed triangles within a set of nodes that are balanced.
    A triangle is balanced if the product of its three edge signs is positive.
    """
    subgraph = G_signed.subgraph(nodes)
    balanced = 0
    total = 0

    for u in subgraph.nodes():
        neighbors = list(subgraph.neighbors(u))
        for i in range(len(neighbors)):
            for j in range(i + 1, len(neighbors)):
                v, w = neighbors[i], neighbors[j]
                if subgraph.has_edge(v, w):  # closed triangle
                    sign_uv = subgraph[u][v]['sign']
                    sign_uw = subgraph[u][w]['sign']
                    sign_vw = subgraph[v][w]['sign']
                    product = sign_uv * sign_uw * sign_vw
                    balanced += 1 if product > 0 else 0
                    total += 1

    return balanced / total if total > 0 else None  # None if no triangles

# Group nodes by community
communities = {}
for node, comm_id in partition.items():
    communities.setdefault(comm_id, []).append(node)

# Compute balance score for each community
results = []
for comm_id, nodes in communities.items():
    score = balance_score(U, nodes)
    results.append({
        'community': comm_id,
        'size': len(nodes),
        'balance_score': score,
        'n_pos_edges': sum(1 for u, v, d in U.subgraph(nodes).edges(data=True) if d['sign'] == 1),
        'n_neg_edges': sum(1 for u, v, d in U.subgraph(nodes).edges(data=True) if d['sign'] == -1),
    })

df_results = pd.DataFrame(results).dropna()  # drop communities with no triangles
df_results = df_results.sort_values('balance_score')

print(df_results.to_string(index=False))

# ── Step 3: Visualize ─────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Balance score distribution
axes[0].hist(df_results['balance_score'], bins=20, color='steelblue', edgecolor='white')
axes[0].axvline(x=0.5, color='red', linestyle='--', label='Random baseline (0.5)')
axes[0].set_title('Balance Score Distribution across Communities')
axes[0].set_xlabel('Balance Score')
axes[0].set_ylabel('Number of Communities')
axes[0].legend()

# Balance score vs community size
axes[1].scatter(df_results['size'], df_results['balance_score'],
                alpha=0.6, color='steelblue')
axes[1].axhline(y=0.5, color='red', linestyle='--', label='Random baseline (0.5)')
axes[1].set_title('Balance Score vs Community Size')
axes[1].set_xlabel('Community Size (nodes)')
axes[1].set_ylabel('Balance Score')
axes[1].legend()

plt.tight_layout()
plt.savefig('experiment1_balance.png', dpi=150)
plt.show()

# ── Step 4: Summary stats ─────────────────────────────────────────────────────
print(f"\nCommunities with balance score computed: {len(df_results)}")
print(f"Mean balance score:   {df_results['balance_score'].mean():.3f}")
print(f"Median balance score: {df_results['balance_score'].median():.3f}")
print(f"Most tense community: size={df_results.iloc[0]['size']:.0f}, score={df_results.iloc[0]['balance_score']:.3f}")
print(f"Most stable community: size={df_results.iloc[-1]['size']:.0f}, score={df_results.iloc[-1]['balance_score']:.3f}")
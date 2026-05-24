# Experiment 3 — Fragmentation Test
# Tests whether communities with low balance scores (high internal tension)
# tend to fragment more when sign-aware detection is applied.

import json
import numpy as np
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from scipy import stats

# ── 1. LOAD GRAPH AND EXPERIMENT 2 PARTITIONS ─────────────────────────────────
print("Loading symmetric graph and historical partitions...")
df = pd.read_csv('wiki_edges_symmetric.csv')
U = nx.Graph()
for _, row in df.iterrows():
    U.add_edge(int(row['node_A']), int(row['node_B']), sign=int(row['sign']))

try:
    with open('partition_unsigned.json', 'r') as f:
        partition_unsigned = {int(k): v for k, v in json.load(f).items()}
    with open('partition_signed.json', 'r') as f:
        partition_signed = {int(k): v for k, v in json.load(f).items()}
except FileNotFoundError:
    raise FileNotFoundError("Could not find partition files. Dump partition_unsigned.json "
                            "and partition_signed.json from Experiment 2 first.")

# ── 2. HELPER: BALANCE SCORE (fast triangle scan, no enumerate_all_cliques) ───
def compute_balance_score(subgraph):
    """
    Fraction of closed triangles whose edge sign product is +1 (balanced).
    Returns None if no triangles exist — caller should filter these out.
    """
    balanced = 0
    total    = 0
    for u in subgraph.nodes():
        neighbors = list(subgraph.neighbors(u))
        for i in range(len(neighbors)):
            for j in range(i + 1, len(neighbors)):
                v, w = neighbors[i], neighbors[j]
                if subgraph.has_edge(v, w):
                    s1 = subgraph[u][v]['sign']
                    s2 = subgraph[u][w]['sign']
                    s3 = subgraph[v][w]['sign']
                    total    += 1
                    balanced += 1 if (s1 * s2 * s3) == 1 else 0
    return balanced / total if total > 0 else None

# ── 3. TRACK FRAGMENTATION PER UNSIGNED COMMUNITY ─────────────────────────────
print("Analyzing community fragmentation dynamics...")

unsigned_communities = {}
for node, comm_id in partition_unsigned.items():
    unsigned_communities.setdefault(comm_id, []).append(node)

MIN_SIZE = 50  # below this, triangle counts are too sparse for reliable balance scores
fragmentation_data = []

for comm_id, nodes in unsigned_communities.items():
    if len(nodes) < MIN_SIZE:
        continue

    subgraph     = U.subgraph(nodes)
    balance_score = compute_balance_score(subgraph)

    if balance_score is None:        # no triangles → skip
        continue

    signed_assignments = [partition_signed[n] for n in nodes if n in partition_signed]
    if not signed_assignments:
        continue

    unique_splits          = set(signed_assignments)
    num_splits             = len(unique_splits)
    counts                 = Counter(signed_assignments)
    largest_piece_ratio    = counts.most_common(1)[0][1] / len(nodes)
    fragmentation_index    = 1.0 - largest_piece_ratio

    neg_edges = sum(1 for u, v, d in subgraph.edges(data=True) if d['sign'] == -1)
    total_edges = subgraph.number_of_edges()

    fragmentation_data.append({
        'unsigned_comm_id':   comm_id,
        'size':               len(nodes),
        'balance_score':      balance_score,
        'num_splits':         num_splits,
        'fragmentation_index': fragmentation_index,
        'neg_ratio':          neg_edges / total_edges if total_edges > 0 else 0,
    })

df_frag = pd.DataFrame(fragmentation_data)

# ── 4. RESULTS TABLE ──────────────────────────────────────────────────────────
print("\n── Fragmentation Summary (sorted by balance score) ──────────────────────")
print(df_frag.sort_values('balance_score').to_string(index=False))
print("─────────────────────────────────────────────────────────────────────────")

# ── 5. CORRELATIONS ───────────────────────────────────────────────────────────
corr_splits,  p_splits  = stats.pearsonr(df_frag['balance_score'], df_frag['num_splits'])
corr_frag,    p_frag    = stats.pearsonr(df_frag['balance_score'], df_frag['fragmentation_index'])

print(f"\nCorrelation: balance score vs number of splits:      r={corr_splits:.4f}  p={p_splits:.4f}")
print(f"Correlation: balance score vs fragmentation index:   r={corr_frag:.4f}  p={p_frag:.4f}")

print("\nInterpretation:")
if corr_frag < -0.3 and p_frag < 0.05:
    print("→ Significant negative correlation: low-balance communities fragment more.")
elif corr_splits < -0.3 and p_splits < 0.05:
    print("→ Low-balance communities split into more pieces, but not necessarily more evenly.")
else:
    print("→ Weak correlation: structural balance alone does not predict the fracture lines.")
    print("  This is still informative — flow-based barriers (CPMap) may operate independently")
    print("  of triangle-level tension.")

# ── 6. VISUALIZE ──────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Balance Score vs Fragmentation Index
sns.scatterplot(
    data=df_frag, x='balance_score', y='fragmentation_index',
    size='size', sizes=(40, 600), alpha=0.7, color='crimson', ax=axes[0]
)
# Trend line via matplotlib (avoids seaborn version issues)
m, b = np.polyfit(df_frag['balance_score'], df_frag['fragmentation_index'], 1) \
    if len(df_frag) > 1 else (0, 0)
x_line = pd.Series([df_frag['balance_score'].min(), df_frag['balance_score'].max()])
axes[0].plot(x_line, m * x_line + b, color='black', linestyle='--', linewidth=1.2)
axes[0].set_title(f'Balance Score vs Fragmentation Index\n(r={corr_frag:.3f}, p={p_frag:.3f})')
axes[0].set_xlabel('Balance Score (higher = more stable)')
axes[0].set_ylabel('Fragmentation Index (higher = more shattered)')
axes[0].grid(True, linestyle='--', alpha=0.4)

# Plot 2: Balance Score vs Number of Splits
sns.scatterplot(
    data=df_frag, x='balance_score', y='num_splits',
    size='size', sizes=(40, 600), alpha=0.7, color='steelblue', ax=axes[1]
)
m2, b2 = np.polyfit(df_frag['balance_score'], df_frag['num_splits'], 1) \
    if len(df_frag) > 1 else (0, 0)
axes[1].plot(x_line, m2 * x_line + b2, color='black', linestyle='--', linewidth=1.2)
axes[1].set_title(f'Balance Score vs Number of Splits\n(r={corr_splits:.3f}, p={p_splits:.3f})')
axes[1].set_xlabel('Balance Score (higher = more stable)')
axes[1].set_ylabel('Number of sub-communities after signed detection')
axes[1].grid(True, linestyle='--', alpha=0.4)

plt.suptitle('Experiment 3 — Fragmentation Test', fontsize=13, y=1.01)
plt.tight_layout()
plt.savefig('experiment3_fragmentation_test.png', dpi=150, bbox_inches='tight')
plt.show()

print(f"\nCommunities analysed: {len(df_frag)}")
print(f"Mean balance score:   {df_frag['balance_score'].mean():.3f}")
print(f"Mean num splits:      {df_frag['num_splits'].mean():.1f}")
print(f"Mean frag index:      {df_frag['fragmentation_index'].mean():.3f}")
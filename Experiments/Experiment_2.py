# Experiment 2 — Detection Sensitivity
# Run CPMap (Infomap) twice on the same graph:
#   - Once ignoring edge signs (unsigned baseline)
#   - Once using signs as edge weights (sign-aware)
# Compare the two partitions using NMI to isolate the effect of negative edges.
# This addresses the reviewer's concern: any difference is purely due to signs,
# not a difference in algorithm choice.

import networkx as nx
import infomap
import pandas as pd
from sklearn.metrics import normalized_mutual_info_score
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
import sys
import pickle


# ── Load graph ────────────────────────────────────────────────────────────────
def load_graph(path):
    if path.endswith(".pkl"):
        with open(path, "rb") as f:
            G = pickle.load(f)
    elif path.endswith(".csv"):
        df = pd.read_csv(path)
        G = nx.Graph()
        for _, row in df.iterrows():
            G.add_edge(row['node_A'], row['node_B'], sign=row['sign'])
    else:
        raise ValueError(f"Unsupported file format: {path}. Use .pkl or .csv")
    
    print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    return G

path = sys.argv[1] if len(sys.argv) > 1 else "signed_ba3.pkl"
U = load_graph(path)
base = path.replace(".pkl", "").replace(".csv", "")

print(f"Graph loaded: {U.number_of_nodes()} nodes, {U.number_of_edges()} edges")

# ── Helper: run Infomap and return partition dict ─────────────────────────────
def run_infomap(G, use_signs=False):
    """
    Run Infomap on graph G.
    If use_signs=True, negative edges get weight -1 (barriers to flow).
    If use_signs=False, all edges get weight 1 (unsigned baseline).
    Returns a dict {node_id: community_id}.
    """
    im = infomap.Infomap('--two-level --silent --seed 42')

    for u, v, data in G.edges(data=True):
        if use_signs:
            weight = data['sign']  # +1 or -1
        else:
            weight = 1             # treat all edges as positive
        im.add_link(u, v, weight)

    im.run()

    partition = {}
    for node in im.tree:
        if node.is_leaf:
            partition[node.node_id] = node.module_id

    return partition

# ── Run CPMap twice ───────────────────────────────────────────────────────────
print("\nRunning CPMap (unsigned)...")
partition_unsigned = run_infomap(U, use_signs=False)

print("Running CPMap (signed)...")
partition_signed = run_infomap(U, use_signs=True)

n_comm_unsigned = len(set(partition_unsigned.values()))
n_comm_signed   = len(set(partition_signed.values()))
print(f"\nCommunities detected (unsigned): {n_comm_unsigned}")
print(f"Communities detected (signed):   {n_comm_signed}")

# ── Compute NMI ───────────────────────────────────────────────────────────────
# Align nodes — only compare nodes present in both partitions
shared_nodes = sorted(set(partition_unsigned) & set(partition_signed))
labels_unsigned = [partition_unsigned[n] for n in shared_nodes]
labels_signed   = [partition_signed[n]   for n in shared_nodes]

nmi = normalized_mutual_info_score(labels_unsigned, labels_signed)
print(f"\nNMI between unsigned and signed CPMap: {nmi:.4f}")
print("(NMI = 1.0 → identical partitions; NMI = 0.0 → completely different)")
if nmi < 0.7:
    print("→ Low NMI: negative edges carry real structural information")
elif nmi < 0.9:
    print("→ Moderate NMI: negative edges cause partial restructuring")
else:
    print("→ High NMI: negative edges have little effect on macro community structure")

# ── Per-node assignment changes ───────────────────────────────────────────────
changed = sum(1 for n in shared_nodes if partition_unsigned[n] != partition_signed[n])
print(f"\nNodes that switched community: {changed} / {len(shared_nodes)} "
      f"({100 * changed / len(shared_nodes):.1f}%)")

# ── Community size distributions ──────────────────────────────────────────────
from collections import Counter

sizes_unsigned = sorted(Counter(partition_unsigned.values()).values(), reverse=True)
sizes_signed   = sorted(Counter(partition_signed.values()).values(), reverse=True)

# ── Visualize ─────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# 1. Community size distribution — unsigned
axes[0].bar(range(len(sizes_unsigned)), sizes_unsigned, color='steelblue', alpha=0.8)
axes[0].set_title(f'CPMap Unsigned\n({n_comm_unsigned} communities)')
axes[0].set_xlabel('Community rank (by size)')
axes[0].set_ylabel('Community size (nodes)')

# 2. Community size distribution — signed
axes[1].bar(range(len(sizes_signed)), sizes_signed, color='tomato', alpha=0.8)
axes[1].set_title(f'CPMap Signed\n({n_comm_signed} communities)')
axes[1].set_xlabel('Community rank (by size)')
axes[1].set_ylabel('Community size (nodes)')

# 3. NMI summary panel
axes[2].barh(['NMI'], [nmi], color='mediumpurple', alpha=0.85)
axes[2].barh(['NMI'], [1 - nmi], left=[nmi], color='lightgrey', alpha=0.6)
axes[2].set_xlim(0, 1)
axes[2].set_title('Partition Similarity (NMI)\nUnsigned vs Signed CPMap')
axes[2].axvline(x=0.5, color='red', linestyle='--', alpha=0.5, label='0.5 threshold')
axes[2].text(nmi / 2, 0, f'{nmi:.3f}', ha='center', va='center',
             fontsize=13, fontweight='bold', color='white')
patch_sim  = mpatches.Patch(color='mediumpurple', alpha=0.85, label='Similarity')
patch_diff = mpatches.Patch(color='lightgrey', alpha=0.6, label='Difference')
axes[2].legend(handles=[patch_sim, patch_diff], loc='lower right')

plt.suptitle('Experiment 2 — Detection Sensitivity: Effect of Negative Edges on Community Structure',
             fontsize=12, y=1.01)
plt.tight_layout()
plt.savefig('experiment2_sensitivity.png', dpi=150, bbox_inches='tight')
plt.show()

# ── Summary table ─────────────────────────────────────────────────────────────
print("\n── Summary ──────────────────────────────────────────────────────")
print(f"  Algorithm:              CPMap (Infomap), run twice")
print(f"  Unsigned communities:   {n_comm_unsigned}")
print(f"  Signed communities:     {n_comm_signed}")
print(f"  NMI:                    {nmi:.4f}")
print(f"  Nodes switching comm.:  {changed} ({100 * changed / len(shared_nodes):.1f}%)")
print("─────────────────────────────────────────────────────────────────")

only_unsigned = set(partition_unsigned) - set(partition_signed)
only_signed   = set(partition_signed)   - set(partition_unsigned)
print(f"Nodes only in unsigned partition: {len(only_unsigned)}")
print(f"Nodes only in signed partition:   {len(only_signed)}")

with open(f'partition_unsigned_{base}.json', 'w') as f: 
    json.dump(partition_unsigned, f)
with open(f'partition_signed_{base}.json', 'w') as f: 
    json.dump(partition_signed, f)
"""
with open('partition_unsigned.json', 'w') as f: json.dump(partition_unsigned, f)
with open('partition_signed.json', 'w') as f: json.dump(partition_signed, f)"""
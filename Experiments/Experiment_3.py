import json
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# ── 1. LOAD GRAPH AND EXPERIMENT 2 PARTITIONS ─────────────────────────────────
print("Loading symmetric graph and historical partitions...")
df = pd.read_csv('wiki_edges_symmetric.csv')
U = nx.Graph()
for _, row in df.iterrows():
    U.add_edge(int(row['node_A']), int(row['node_B']), sign=int(row['sign']))

try:
    with open('partition_unsigned.json', 'r') as f:
        # JSON keys are always strings; convert them back to integer node IDs
        partition_unsigned = {int(k): v for k, v in json.load(f).items()}
    with open('partition_signed.json', 'r') as f:
        partition_signed = {int(k): v for k, v in json.load(f).items()}
except FileNotFoundError:
    raise FileNotFoundError("Could not find partition files. Make sure you dumped "
                            "partition_unsigned.json and partition_signed.json from Exp 2!")

# ── 2. HELPER: CALCULATE STRUCTURAL BALANCE SCORE ──────────────────────────────
def compute_balance_score(subgraph):
    """
    Computes the fraction of internal triangles that are structurally balanced 
    (product of edge signs == +1). Returns 1.0 if no triangles exist.
    """
    triangles = nx.triangles(subgraph)
    # Get unique triadic node sets to avoid double counting triangles
    all_triads = [set(t) for t in nx.enumerate_all_cliques(subgraph) if len(t) == 3]
    
    if not all_triads:
        return 1.0  # Default to stable if no local triads exist to cause tension
        
    balanced_count = 0
    for triad in all_triads:
        nodes = list(triad)
        s1 = subgraph[nodes[0]][nodes[1]]['sign']
        s2 = subgraph[nodes[1]][nodes[2]]['sign']
        s3 = subgraph[nodes[2]][nodes[0]]['sign']
        
        if (s1 * s2 * s3) == 1:
            balanced_count += 1
            
    return balanced_count / len(all_triads)

# ── 3. TRACK FRAGMENTATION PER UNSIGNED COMMUNITY ─────────────────────────────
print("\nAnalyzing community fragmentation dynamics...")

# Group nodes by their original unsigned community ID
unsigned_communities = {}
for node, comm_id in partition_unsigned.items():
    unsigned_communities.setdefault(comm_id, []).append(node)

fragmentation_data = []

for comm_id, nodes in unsigned_communities.items():
    if len(nodes) < 10: 
        continue  # Skip tiny singletons/cliques to filter structural noise
        
    subgraph = U.subgraph(nodes)
    
    # Measure Internal Tension (Experiment 1 property)
    balance_score = compute_balance_score(subgraph)
    
    # Track how many distinct signed communities these same nodes split into
    # We only look at nodes that survived into the signed partition
    signed_assignments = [partition_signed[n] for n in nodes if n in partition_signed]
    
    if not signed_assignments:
        continue
        
    unique_splits = set(signed_assignments)
    num_splits = len(unique_splits)
    
    # Calculate an entropy or a size-based fragmentation index
    # (How cleanly did it crack? Did 1 node leave, or did it split 50/50?)
    counts = Counter(signed_assignments)
    largest_piece_ratio = counts.most_common(1)[0][1] / len(nodes)
    fragmentation_index = 1.0 - largest_piece_ratio # Higher means more shattered
    
    fragmentation_data.append({
        'unsigned_comm_id': comm_id,
        'size': len(nodes),
        'balance_score': balance_score,
        'num_splits': num_splits,
        'fragmentation_index': fragmentation_index
    })

df_frag = pd.DataFrame(fragmentation_data)

# ── 4. ANALYSIS & STATISTICAL CORRELATION ────────────────────────────────────
print("\n── Fragmentation Summary Table ──────────────────────────")
print(df_frag.sort_values(by='balance_score').head(10).to_string(index=False))
print("─────────────────────────────────────────────────────────")

# Compute Pearson Correlation between Balance (Stability) and Fragmentation
corr_splits = df_frag['balance_score'].corr(df_frag['num_splits'])
corr_shatter = df_frag['balance_score'].corr(df_frag['fragmentation_index'])

print(f"\nCorrelation between Balance Score and Number of Splits: {corr_splits:.4f}")
print(f"Correlation between Balance Score and Fragmentation Index: {corr_shatter:.4f}")
print("\nInterpretation:")
if corr_shatter < -0.3:
    print("→ Strong Negative Correlation: Confirmed! Low balance scores (high tension) "
          "\n  directly drive communities to shatter into pieces.")
else:
    print("→ Weak/No Correlation: Structural balance alone might not dictate the specific "
          "\n  fracture lines found by the flow model.")

# ── 5. VISUALIZE RESULTS ──────────────────────────────────────────────────────
plt.figure(figsize=(10, 5))

# Scatter plot: Balance Score vs Fragmentation Index
sns.scatterplot(data=df_frag, x='balance_score', y='fragmentation_index', 
                size='size', sizes=(20, 400), alpha=0.7, color='crimson')

plt.title('Experiment 3 — Fragmentation Test\nDoes Low Community Balance Trigger Structural Shattering?', fontsize=12)
plt.xlabel('Community Balance Score (Exp 1 Metric — Higher means more balanced/stable)')
plt.ylabel('Fragmentation Index (Exp 2 Outcome — Higher means more shattered)')
plt.grid(True, linestyle='--', alpha=0.5)

# Add trend line
sns.regplot(data=df_frag, x='balance_score', y='fragmentation_index', 
            scatter=False, color='black', linestyle='--')

plt.tight_layout()
plt.savefig('experiment3_fragmentation_test.png', dpi=150)
plt.show()
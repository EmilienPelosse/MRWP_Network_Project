import networkx as nx
import pandas as pd
import numpy as np

def extract_network_metrics(csv_path):
    print(f"Reading preprocessed dataset from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # 1. Reconstruct the Undirected Graph (U)
    U = nx.Graph()
    for _, row in df.iterrows():
        U.add_edge(int(row['node_A']), int(row['node_B']), sign=int(row['sign']))
        
    # 2. Extract Fundamental Counts
    N = U.number_of_nodes()
    E = U.number_of_edges()
    
    # 3. Calculate Density and Degree Properties
    density = nx.density(U)
    degrees = [d for _, d in U.degree()]
    avg_degree = np.mean(degrees)
    
    # 4. Extract Sign Statistics
    pos_edges = sum(1 for _, _, d in U.edges(data=True) if d['sign'] == 1)
    neg_edges = sum(1 for _, _, d in U.edges(data=True) if d['sign'] == -1)
    
    pos_ratio = pos_edges / E
    neg_ratio = neg_edges / E
    
    # 5. Calculate the BA Model Parameter 'm'
    # E = m * (N - m) roughly, or simpler: m = round(E / N)
    m_estimated = round(E / N)
    
    # Safeguard check: m must be >= 1 and < N
    m_estimated = max(1, m_estimated)

    # ── PRINT PRODUCTION REPORT ───────────────────────────────────────────────
    print("\n" + "="*45)
    print("      WIKIELEC STRUCTURAL BASELINE REPORT     ")
    print("="*45)
    print(f"Nodes (N):               {N}")
    print(f"Edges (E):               {E}")
    print(f"Network Density:         {density:.5f}")
    print(f"Average Node Degree:     {avg_degree:.2f}")
    print("-"*45)
    print(f"Positive Edges Count:    {pos_edges} ({pos_ratio:.2%})")
    print(f"Negative Edges Count:    {neg_edges} ({neg_ratio:.2%})")
    print("-"*45)
    print("TARGET PARAMETERS FOR YOUR EXP 4 BA MODEL")
    print(f"  n (Total Nodes to grow)  = {N}")
    print(f"  m (Edges per new node)   = {m_estimated}")
    print(f"  Base Distrust Rate       = {neg_ratio:.4f} (~{neg_ratio*100:.1f}%)")
    print("="*45)
    
    return {
        'n': N,
        'm': m_estimated,
        'neg_ratio': neg_ratio
    }

if __name__ == "__main__":
    # Ensure this file matches the output path from your preprocessing step
    CSV_FILE = 'wiki_edges_symmetric.csv'
    
    try:
        metrics = extract_network_metrics(CSV_FILE)
    except FileNotFoundError:
        print(f"\n[Error] Missing '{CSV_FILE}'. Run your preprocessing script first!")
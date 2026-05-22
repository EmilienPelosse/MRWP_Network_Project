import networkx as nx
import random

results = []

for i in range(100) :

    G = nx.barabasi_albert_graph(n=100, m=2)

    for u, v in G.edges():
        r = random.random()      # random float between 0 and 1
        if r < 0.7:
            G[u][v]['sign'] = 1  # 70% chance of positive
        else:
            G[u][v]['sign'] = -1 # 30% chance of negative

    #results.append(my_metric)

    #for u, v, data in G.edges(data=True):
    #    print(f"Edge {u}--{v} : sign = {data['sign']}")

average = sum(results)/len(results)

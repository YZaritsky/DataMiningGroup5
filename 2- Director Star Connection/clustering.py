import os
import pandas as pd
import networkx as nx
from sklearn.cluster import SpectralClustering
import matplotlib.pyplot as plt
import numpy as np

os.makedirs('./output', exist_ok=True)

data = pd.read_csv('./data/imdb-movies-dataset.csv')

director_counts = data['Director'].value_counts()
directors = director_counts[director_counts >= 20].index

B = nx.Graph()
B.add_nodes_from(directors, bipartite=0)
actors = set(actor for cast in data['Cast'].dropna() for actor in cast.split(', '))
B.add_nodes_from(actors, bipartite=1)

for director, cast in zip(data['Director'], data['Cast']):
    if pd.notna(cast) and director in directors:
        B.add_edges_from((director, actor) for actor in cast.split(', ') if actor != director)

top_directors = sorted(directors, key=lambda x: B.degree(x), reverse=True)
top_actors = set(actor for director in top_directors for actor in B.neighbors(director))

subgraph = B.subgraph(top_directors + list(top_actors))
print(f"Subgraph has {subgraph.number_of_nodes()} nodes and {subgraph.number_of_edges()} edges")

if subgraph.number_of_nodes() and subgraph.number_of_edges():
    adj_matrix = nx.adjacency_matrix(subgraph)
    labels = SpectralClustering(n_clusters=5, affinity='precomputed', random_state=42).fit_predict(adj_matrix.toarray())

    pos = nx.spring_layout(subgraph, seed=42, k=0.1)
    plt.figure(figsize=(14, 12))

    director_positions = {node: pos[node] for node in top_directors}
    actor_positions = {node: pos[node] for node in top_actors}

    unique_labels = np.unique(labels)
    colors = plt.cm.tab10(unique_labels)

    for label, color in zip(unique_labels, colors):
        director_cluster = [node for node, lab in zip(subgraph.nodes(), labels) if
                            lab == label and node in top_directors]
        actor_cluster = [node for node, lab in zip(subgraph.nodes(), labels) if lab == label and node in top_actors]

        if director_cluster:
            plt.scatter(*zip(*[pos[node] for node in director_cluster]), s=500, color=color, edgecolors='k')
        if actor_cluster:
            plt.scatter(*zip(*[pos[node] for node in actor_cluster]), s=50, color=color, alpha=0.6)

    nx.draw_networkx_edges(subgraph, pos, alpha=0.5)

    for director in top_directors:
        plt.text(pos[director][0], pos[director][1] + 0.03, director, fontsize=10, ha='center', va='bottom',
                 fontweight='bold', bbox=dict(facecolor='white', alpha=0.5, edgecolor='none'))

    plt.title('Top 10 Directors-Actor Connections with Clustering')
    plt.xlabel('')
    plt.ylabel('')
    plt.savefig('./output/directors_actors_clustering.png')
    plt.show()
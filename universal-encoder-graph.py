import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from sklearn.cluster import KMeans
import tensorflow as tf
import plotly.graph_objects as go

data = pd.read_csv("all_results.csv")
titles = data["Title"]

# Load the Universal Sentence Encoder model
model_path = "/home/core/model/"
embed = tf.saved_model.load(model_path)

# Generate sentence embeddings based on the rsrch titles
title_embeddings = embed(titles)

# Number of clusters
num_clusters = 10

# K-Means clustering
kmeans = KMeans(n_clusters=num_clusters)
kmeans.fit(title_embeddings)

# Labels
data['Cluster'] = kmeans.labels_

# Save to csv
data.to_csv("clustered_titles.csv", index=False)

clustered_data = pd.read_csv("clustered_titles.csv")

# Create a directed graph
G = nx.DiGraph()

# Cluster nodes
for cluster_id in clustered_data['Cluster'].unique():
    G.add_node(cluster_id, type='cluster')

# Ttile nodes
for index, row in clustered_data.iterrows():
    title = row['Title']
    cluster_id = row['Cluster']
    G.add_node(title, type='Title', cluster=cluster_id)

# Edges
for index, row in clustered_data.iterrows():
    title = row['Title']
    cluster_id = row['Cluster']
    G.add_edge(cluster_id, title)

# <<-----------------Plotly-------------------->> #
pos = nx.spring_layout(G, seed=42)
edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(None)
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines')

node_x = []
node_y = []
for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        colorscale='YlGnBu',
        size=10,
    ))

node_adjacencies = []
node_text = []
for node, adjacencies in enumerate(G.adjacency()):
    node_adjacencies.append(len(adjacencies[1]))
    node_text.append('# of connections: ' + str(len(adjacencies[1])))

node_trace.marker.color = node_adjacencies
node_trace.text = node_text

# Plotly
fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    showlegend=True,
                    hovermode='closest',
                    margin=dict(b=0, l=0, r=0, t=0),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )

fig.show()

# Save to html
fig.write_html("interactive_network.html")

clustered_data.to_csv("clustered_titles_with_clusters.csv", index=False)

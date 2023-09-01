import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.decomposition import PCA

data = pd.read_csv("all_results.csv")

data['Title'] = data['Title'].str.lower().str.replace('[^\w\s]', '')  # Convert to lowercase and remove punctuation

# TF-IDF vectors
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(data['Title'])

# Hierarchical clustering
linkage_matrix = linkage(tfidf_matrix.toarray(), method='ward', metric='euclidean')
dendrogram_labels = dendrogram(linkage_matrix, truncate_mode='lastp', p=10, leaf_rotation=90)

# Number of clusters
num_clusters = len(set(dendrogram_labels['color_list']))

# Agglomerative clustering to cluster publications
agg_clustering = AgglomerativeClustering(n_clusters=num_clusters)
clusters = agg_clustering.fit_predict(tfidf_matrix.toarray())

# Label
data['cluster'] = clusters

# Save clustered data to csv
clustered_data = data[['Title', 'cluster']]
clustered_data.to_csv("clustered_publications.csv", index=False)

# PCA
pca = PCA(n_components=2)  # You can change the number of components
reduced_features = pca.fit_transform(tfidf_matrix.toarray())

# Scatter plot
plt.figure(figsize=(10, 8))
plt.scatter(reduced_features[:, 0], reduced_features[:, 1], c=clusters, cmap='rainbow', s=50)  # Adjust 's' to control size
plt.title("Clustered Publications")
plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")

# Annotate
for i, (x, y) in enumerate(reduced_features):
    plt.annotate(f"Row {i+1}", (x, y))

plt.show()

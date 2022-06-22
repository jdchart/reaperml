from sklearn.manifold import TSNE
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import Normalizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import umap
import matplotlib.pyplot as plt
import random
import utils

def tsne_transform(arr, **kwargs):

    tsne = TSNE(n_components = kwargs.get('dimensions', 2))
    reduced = tsne.fit_transform(arr)

    return reduced

def umap_transform(arr, **kwargs):
    reducer = umap.UMAP(n_components = kwargs.get('dimensions', 2))
    reduced = reducer.fit_transform(arr)
    reduced.shape

    return reduced

def nearest_neighbour(arr, query, **kwargs):
    # TO DO choice return index/content?
    neigh = NearestNeighbors(n_neighbors = kwargs.get('num_neighbors', 1))
    neigh.fit(arr)

    result =  neigh.kneighbors([query])

    point_index_array = result[1][0]
    distance_array = result[0][0]

    return point_index_array

def standardize(arr):

    scaled = StandardScaler().fit_transform(arr)

    return scaled

def normalize(arr):
    normed = Normalizer().fit_transform(arr)

    return normed

def min_max(arr, **kwargs):
    scaled = MinMaxScaler((kwargs.get('min', 0), kwargs.get('max', 1))).fit_transform(arr)

    return scaled

def cluster(arr, **kwargs):

    kmeans = KMeans(n_clusters = kwargs.get('num_clusters', 2), random_state=0) 
    clustered = kmeans.fit(arr) 

    # kmeans.cluster_centers_
    # kmeans.predict([[0, 0], [12, 3]])

    return clustered.labels_

def display_np(arr, **kwargs):
    axes   = kwargs.get('axes', [0, 1])
    clusters = kwargs.get('cluster_data', [])
    title = kwargs.get('title', 'Graph')

    fig, ax = plt.subplots()

    if len(clusters) != 0:
        col_map = get_colour_map(clusters)

    x_axis = []
    y_axis = []
    col    = []

    for i in range(len(arr)):
        x_axis.append(arr[i][axes[0]])
        y_axis.append(arr[i][axes[1]])
        if len(clusters) != 0:
            pass
            col.append(find_col(clusters[i], col_map))
        else:
            col.append((1.0, 0.0, 0.0))

    ax.scatter(x_axis, y_axis, c=col)
    
    fig.tight_layout()

    #plt.title(title)
    #fig.figure(num=title)

    plt.show()

def cluster_sort(content, clusters):
    individual_items = get_cluster_arrat(clusters)
    return_array = utils.create_empty_2d_array(len(individual_items))

    for i in range(len(content)):
        this_entry = content[i]
        this_cluster = clusters[i]
        return_array[this_cluster].append(this_entry)

    return return_array

def find_col(item, col_map):
    for col in col_map:
        if item == col[0]:
            return col[1]

def get_colour_map(cluster_array):
    individual_items = get_cluster_arrat(cluster_array)
    to_return = []

    for item in individual_items:
        to_return.append([item, (random.random(), random.random(), random.random())])

    return to_return

def get_cluster_arrat(cluster_array):
    individual_items = []
    for item in cluster_array:
        if item not in individual_items:
            individual_items.append(item)

    return individual_items
# Here, we shall perform dimensionality reduction on a collection, find clusters in this reduction,
# and visualisae the results.

from _reaperml_lib import *

# Loading the collection of sounds:
file = '/Users/macbook/Desktop/TESTTEST/Z_COLLECTION/collection.json'
loadedCollection = fluid.Collection(file = file)

# Convert the desired descriptors to a numpy array.
# The first column will be the index of the slice.
desc_np = loadedCollection.descriptors_to_np([{'process_name' : 'mfcc'}])

# We'll first standardize the data
standardized_data = ml.standardize(desc_np[:,1:])

# Then reduce this data to 2 dimensions using tsne:
reduced_data = ml.tsne_transform(standardized_data)

# First, we shall display this reduced data:
ml.display_np(reduced_data)

# Next, we can find clusters in this data:
clusters = ml.cluster(reduced_data, num_clusters = 10)

# And finally display this data again with the cluster_data assigned to the clusters.
ml.display_np(reduced_data, cluster_data = clusters)
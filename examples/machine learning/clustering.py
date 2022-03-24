# Find clusters of slices in a collection of sounds.

from _reaperml_lib import *

# Loading the collection of sounds:
file = '/Users/macbook/Documents/BACKUP_GIT/jh-musicking/reaperml/output2/collection.json'
loadedCollection = fluid.Collection(file = file)

# Convert the desired descriptors to a numpy array.
# The first column will be the index of the slice.
desc_np = loadedCollection.descriptors_to_np([{'process_name' : 'mfcc'}])

# Calculate the clusters (without the first column):
clusters = ml.cluster(desc_np[:,1:], num_clusters = 4)

# See the results (an array where each entry corresponds to each slice's cluster index in order)
print(clusters)

# Sort the slices into their various clusters:
clusters_sorted = ml.cluster_sort(desc_np, clusters)

# Print out the slice indexes of each cluster:
print('Number of clusters: ' + str(len(clusters_sorted)) + '.')
for cluster in clusters_sorted:
    print_string = ""
    for item in cluster:
        print_string = print_string + str(item[0]) + " "
    print(print_string + '\n')
# In this project, we shall first load a collection of sounds, and find different clusters in this collection.
# Then, we shall export this data into a reaper project, where each track contains the elements of each cluster.

from _reaperml_lib import *
import os

# Decide how many clusters of slices you wish to find:
num_clusters = 10

# Load a collection and gather the descriptor data to use for calculating clusters:
file = '/Users/macbook/Desktop/TESTTEST/Z_COLLECTION/collection.json'
loadedCollection = fluid.Collection(file = file)
desc_np = loadedCollection.descriptors_to_np([{'process_name' : 'mfcc'}])

# Get the cluster data (performing standardizeation and data reduction first):
standardized_data = ml.standardize(desc_np[:,1:])
reduced_data = ml.tsne_transform(standardized_data)
clusters = ml.cluster(reduced_data, num_clusters = num_clusters)

# Sort the original data into an array for each cluster:
cluster_sorted = ml.cluster_sort(desc_np, clusters)

# Create a project, and a track for each cluster:
cluster_project = reaper.Project()
for _ in cluster_sorted:
    cluster_project.add(reaper.Track())

for i in range(len(cluster_sorted)):
    # Get the next track that was previously created:
    this_track = cluster_project.get_tracks()[i]

    # Reset the playhead position at the beginning of each track:
    current_playhead = 0
    
    # Iterate through items in each cluster:
    for item in cluster_sorted[i]:
        # Get the slice (the index is the first element of the desc_np entries, 
        # and is a float so needs to be converted):
        this_slice = fluid.Slice(loadedCollection.slices[int(item[0])])

        # Get the length of the slice (converted to reaper unit):
        len_in_reaper = cluster_project.time_convert('samps', 'reaper', this_slice.num_frames)
        
        # And add the item to the current track:
        this_track.add(reaper.Item(
            reaper.Source(file = this_slice.path),
            position = current_playhead,
            length = len_in_reaper
        ))

        # Finally move the playhead:
        current_playhead = current_playhead + len_in_reaper

# Write the project out to file:
cluster_project.write('/Users/macbook/Desktop/TESTTEST/clusters.rpp')
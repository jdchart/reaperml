# Perform nearest neighbour searches.

from _reaperml_lib import *

# Loading the collection of sounds:
file = '/Users/macbook/Documents/BACKUP_GIT/jh-musicking/reaperml/output2/collection.json'
loadedCollection = fluid.Collection(file = file)

# Convert the desired descriptors to a numpy array.
# The first column will be the index of the slice.
desc_np = loadedCollection.descriptors_to_np([{'process_name' : 'mfcc'}])

# Here we are looking for the nearest neighbour in the desc_np collection
# to entry 2 of the desc_np collection.
# So the nearest neighbour, should be entry 2 of the collection.
# It is the index of the desc_np entry that is returned:
nearest_neighbour = ml.nearest_neighbour(desc_np[:,1:], desc_np[:,1:][2])
print(nearest_neighbour)

# But we can also see what are the other nearest neighbours:
nearest_neighbour_list = ml.nearest_neighbour(desc_np[:,1:], desc_np[:,1:][2], num_neighbors = 5)
print(nearest_neighbour_list)
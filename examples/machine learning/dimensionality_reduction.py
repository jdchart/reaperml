# Here, we shall reduce multi-dimensional data down to any number of dimensions
# using dimensionality reduction.

from _reaperml_lib import *

# Loading the collection of sounds:
file = '/Users/macbook/Documents/BACKUP_GIT/jh-musicking/reaperml/output2/collection.json'
loadedCollection = fluid.Collection(file = file)

# Convert the desired descriptors to a numpy array.
# The first column will be the index of the slice.
desc_np = loadedCollection.descriptors_to_np([{'process_name' : 'mfcc'}])

# See what the original data was:
print(desc_np)

# Reduce it using tsne, and see the results:
reduced_data_tsne = ml.tsne_transform(desc_np[:,1:])
print(reduced_data_tsne)

# Another data reduction aglorithm is UMAP:
reduced_data_umap = ml.umap_transform(desc_np[:,1:], dimensions = 3)
print(reduced_data_umap)
# Process grouped data.

from _reaperml_lib import *

# Loading the collection of sounds:
file = '/Users/macbook/Documents/BACKUP_GIT/jh-musicking/reaperml/output2/collection.json'
loadedCollection = fluid.Collection(file = file)

# Convert the desired descriptors to a numpy array.
# The first column will be the index of the slice.
desc_np = loadedCollection.descriptors_to_np([{'process_name' : 'mfcc'}])

# See what the data looks like originally:
print(desc_np)

# Perform standardization on the data:
standardized_data = ml.standardize(desc_np[:,1:])
print(standardized_data)

# Or perform normalization on the data:
normalized_data = ml.normalize(desc_np[:,1:])
print(normalized_data)
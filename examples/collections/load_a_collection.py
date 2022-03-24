# Loading a collection.

from _reaperml_lib import *

# The .json file of the collection to load:
file = '/Users/macbook/Documents/BACKUP_GIT/jh-musicking/reaperml/output/collection.json'
loadedCollection = fluid.Collection(file = file)

# Print out the collection:
print(loadedCollection)

# Printing out the description for each slice in the collection:
for slice in loadedCollection.slices:
    this_slice = fluid.Slice(slice)
    for desc in this_slice.descriptions:
        print(desc)
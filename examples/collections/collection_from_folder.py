# Create and write a fluid collection from a folder of sound files, or of slices.

from _reaperml_lib import *
import os

# The path to the folde rto use for the collection:
folder_path = '/Users/macbook/Desktop/corptest'

# Get a list of either sound files, or slice files (.json) in that folder:
file_list = ut.get_files(folder_path, mode = 'path')
# file_list = ut.get_files(test_folder, mode = 'path', types = ['.json'])

# The collection that will contain the slices:
myCollection = fluid.Collection()

# Add a list of slices to the collection and print the collection to see if everything worked:
myCollection.append_slices(file_list)
print(myCollection)

# Run some descriptions on the collection:
myCollection.describe('pitch')
myCollection.describe('loudness')
myCollection.describe('mfcc')

# And finally, write everything to file.
# Give the collection file name, and if needed, slice files will be created in the same directory:
myCollection.write(os.path.join(os.getcwd(), 'data/COLLECTION_FOLDER/my_collection_file.json'))
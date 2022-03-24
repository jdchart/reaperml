# Create a collection of content in a reaper project.

from _reaperml_lib import *
import os

# Load a reaper project into reathon:
rpp_file = '/Users/macbook/Documents/BACKUP_GIT/jh-musicking/reaperml/tes_proj_sliced.RPP'
myProject = reaper.Project(file = rpp_file)

# You can create a collection with various filters.
# This will create a collection from every media item:
reaper_collection = myProject.convert_to_collection()

# This will create a collection with only the items in tracks 0 and 1:
#reaper_collection = myProject.convert_to_collection(tracks = [0, 1])

# This will create a collection only with selected items:
#reaper_collection = myProject.convert_to_collection(filter_selected = True)

# And this will create a colltion with only selected items in track 2:
#reaper_collection = myProject.convert_to_collection(tracks = [2], filter_selected = True)

# Print the collection to check that everything has worked:
print(reaper_collection)

# Run a description on the collection:
reaper_collection.describe('pitch')

# Output the collection to file:
reaper_collection.write(os.path.join(os.getcwd(), 'data/OUTPUT_FOLDER/collection_name.json'))

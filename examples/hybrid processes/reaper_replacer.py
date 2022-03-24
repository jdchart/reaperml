# Replace content from an existing reaper project with content from a collection
# using nearest neighbour searches.

from _reaperml_lib import *
import os

# Load the reaper project:
rpp_file = '/Users/macbook/Documents/BACKUP_GIT/jh-musicking/reaperml/replacer_source.RPP'
myProject = reaper.Project(file = rpp_file)

# Convert the items in track 0 to a collection, and describe them with mfcc:
reaper_collection = myProject.convert_to_collection(tracks = [0])
reaper_collection.describe('mfcc')

# Loading a collection for replacing:
new_slices_path = '/Users/macbook/Documents/BACKUP_GIT/jh-musicking/reaperml/output2/collection.json'
collection_for_replacing = fluid.Collection(file = new_slices_path)

# Retrieve the mfcc description of this collection:
collection_for_replacing_description = collection_for_replacing.descriptors_to_np([{'process_name' : 'mfcc'}])

# Create a new track which will contain the new items:
adding_track = reaper.Track()

# Iterate through the slices in the reaper collection:
for slice in reaper_collection.slices:
    # Load the slice and get it's mfcc description:
    this_slice = fluid.Slice(slice)
    this_slice_data = this_slice.descriptions[0].data
    
    # Run the nearest neighbour search:
    nn_idx = ml.nearest_neighbour(collection_for_replacing_description[:,1:], this_slice_data)
    
    # Load the nearest neighbour:
    nearest = fluid.Slice(collection_for_replacing.slices[nn_idx[0]])
    
    # Add the nearest neighbour to the adding track:
    adding_track.add(reaper.Item(
        reaper.Source(file = nearest.path),
        position = this_slice.custom_params["reaper_position"],
        length = myProject.time_convert('samps', 'reaper', nearest.num_frames)
    ))

# Add the adding track to the project, then write the project to file:
myProject.add(adding_track)
myProject.write(os.path.join(os.getcwd(), 'data/REPLACER_export.rpp'))
# Load an existing reaper project and access the content of a track.
# Then either duplicate it to a new track, or replace it.

from _reaperml_lib import *
import os
import random

# Load the reaper project:
rpp_file = '/Users/macbook/Documents/BACKUP_GIT/jh-musicking/reaperml/tes_proj_sliced.RPP'
myProject = reaper.Project(file = rpp_file)

# Get a list of the items in track 0:
items_in_track = myProject.get_tracks()[0].get_items()

# A list of files to use for replacing:
to_replace = ut.get_files("/Users/macbook/Documents/Music/Sonic Academy 1.5GB Sign Up Pack/Synthwave/Bass",types = ['.wav', '.aif'], mode = 'path')

# Iterate through each of the items in the track:
for item in items_in_track:
    # For duplication, use the original filename.
    # For replacing, choose a random file in the filelist:
    the_source = item.get_source().get_prop('file')
    # the_source = to_replace[random.randint(0, len(to_replace) - 1)]

    # Add a new item to track 1 (this also assumes that a track for writing the new content already exists).
    # We use the original item's props to define length, position, and if duplicate, offset:
    added_item = myProject.get_tracks()[1].add(
        reaper.Item(
            reaper.Source(file = the_source),
            length = float(item.get_prop('length')),
            position = float(item.get_prop('position')),
            soffs = float(item.get_prop('SOFFS'))
        )
    )

# Finally, write the project to a new file:
myProject.write(os.path.join(os.getcwd(), 'data/duplicated_track.rpp'))
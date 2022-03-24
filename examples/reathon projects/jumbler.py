# Use reathon to generate a project with one track that is filled with a certain number of
# items that are randomly selected from a folder of sound files.

from _reaperml_lib import *
import os
import random

# The files to jumble as a list of sound files:
jumble_source_folder = "/Users/macbook/Desktop/corptest"
sound_files = ut.get_files(jumble_source_folder, mode = 'path')

# The number of items to add to the project:
num_items = 500

# The reathon project and track that the items will be added to:
myProject = reaper.Project()
myTrack = reaper.Track()

current_reaper_cursor = 0
for _ in range(num_items):
    # Choose a random sound file and remove it from the lsit so it isn't chosen again:
    this_source_path = sound_files[random.randint(0, len(sound_files) - 1)]
    sound_files.remove(this_source_path)

    # Get the sound file's metadata, and convert it's length (in ms) to reaper unit:
    meta = ut.process_meta_data(this_source_path)
    length_in_reaper = myProject.time_convert('ms', 'reaper', meta['ms'])
    
    # Create an item and source at the current cursor position, also generate a random pan:
    the_item = reaper.Item(
        reaper.Source(file = this_source_path),
        length = length_in_reaper,
        position = current_reaper_cursor,
        volpan = '1 ' + str(random.randint(-1000, 1000) / 1000)
    )

    # Add the item to the track, and update the current cursor position:
    myTrack.add(the_item)
    current_reaper_cursor = current_reaper_cursor + length_in_reaper

# Add the track to the project, then write the project to file:
myProject.add(myTrack)
myProject.write(os.path.join(os.getcwd(), 'data/jumbled.rpp'))
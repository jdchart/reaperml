# Use reathon to read and write a reaper project (.rpp)

from _reaperml_lib import *
import os

# The .rpp file to read in:
rpp_file = '/Users/macbook/Documents/BACKUP_GIT/reaperml/data/test_proj.RPP'

# Create the reaper project in reathon:
myProject = reaper.Project(file = rpp_file)
# Alternatively, create the project, then read the file=:
# myProject = reaper.Project()
# myProject.read(rpp_file)

# Here, we're adding 100 tracks to the project:
for i in range(100):
    myProject.add(reaper.Track())

# Here, we're adding an item to track 50 of length 5 and position 1.5 (the unit os reaper time):
myProject.get_tracks()[50].add(reaper.Item(length=5, position=1.5))

# Here we can see what the project looks like:
# print(myProject)

# We can print and set transport info, as well as convert different formats.
# Printing:
print(myProject.transport_info["bpm"])
print(myProject.transport_info["time_sig_top"])
print(myProject.transport_info["time_sig_bottom"])

# Setting:
myProject.set_transport_info("bpm", 135)
print(myProject.transport_info["bpm"])

# Converting:
print(myProject.time_convert('beat', 'ms', 50.0))
print(myProject.time_convert('ms', 'reaper', 50.0))
print(myProject.time_convert('reaper', 'beat', 50.0))

# Finally, we can write our project out to a file:
myProject.write(os.path.join(os.getcwd(), 'data/test_export.rpp'))
# Even if this will generally be handled by collections, this shows how to manage slices.

from _reaperml_lib import *
import os

# The audio file path for the slice:
test_file = '/Users/macbook/Documents/BACKUP_GIT/jh-musicking/Media/Nicol-LoopE-M.wav'

# Create the slice. We can define a start and end frame (-1 meaning until the end).
# Alternatively we can give num_frames (-1 also until the end), which will always take priority:
mySlice = fluid.Slice(test_file, name_suffix = 'loool', start_frame = 0, end_frame = -1)

# Print information about the slice:
print(mySlice)

# Run some descriptions on the slice:
mySlice.describe('mfcc')
mySlice.describe('pitch')
mySlice.describe('loudness')

# Now see how the information about the slice changes:
print(mySlice)

# You can also print out information about the descriptions.
for desc in mySlice.descriptions:
    print(desc)

# Finally write the slice to file:
mySlice.write(os.path.join(os.getcwd(), '/data/slice_out.json'))

# A slice can also be read:
to_load = os.path.join(os.getcwd(), '/data/slice_out.json')
loadedSlice = fluid.Slice(to_load)

# Print to check that everything is working:
print(loadedSlice)
for desc in loadedSlice.descriptions:
    print(desc)
    print(desc.data)
# reaperml
Python scripts for musicking with [Reaper](https://www.reaper.fm/) and machine learning.

This is mainly for personal use, but I imagine some people could be interested. Like most things I do, this is essentially a wrapper for other talented people's work - notably [James Bradbury](https://github.com/jamesb93), the [FluCoMa](https://www.flucoma.org/) team and the [scikit-learn](https://scikit-learn.org/stable/) team.

These scripts are an environment for me to do musicking in Reaper using various machine learning algorithms, signal decomposition, algorithmic composition techniques etc.

## Main Features

- Programatically create and modify reaper projects (_.rpp_ files). This is using my modified version of James Bradbury's [reathon](https://github.com/jamesb93/reathon).
- Control audio corpora: create and manipulate collections of sounds and notably their audio descriptions. This is my own, much simpler version of a wrapper around the [FluCoMa](https://www.flucoma.org/) tools, again inspired by James Bradbury's [work](https://github.com/jamesb93/ftis) (honestly, check that guy out).
- Coupling of these elements with my own scikit-learn wrapper. This isn't essential, but I like to think as little as possible about what I'm doing, so look forward to simple functions like `cluster(num_clusters = 4)` or `reduce(method = 'umap', dimensions = 2`.

## Getting Started & Installation

There is no installation because I'm a savage. However, I do recommend you use a [Python virtual environment](https://docs.python.org/3/tutorial/venv.html), and install the [FluCoMa CLI tools](https://github.com/flucoma/flucoma-cli) in this environment's bin.

Then you will need to `pip install` the following dependencies:
- scikit-learn
- soundfile
- numpy
- matplotlib

Oh yeah, and I imagine this will only work in Python 3.7+. I also recommend using something like [Visual Studio Code](https://code.visualstudio.com/) to run this from.

## An Example

As I can't be arsed to do a proper tutorial at the moment, here's how you would use reaperml to open a Reaper project, load a collection of sounds, run a nearest-neighbour search between each item in a certain track in the reaper project with the new collection, create a new track with these new sounds, and save the reaper project:

```python
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
```
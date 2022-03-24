# This wraps up the code needed to run reaperml.
# Just use `from reaperml_lib import *` to access the various elements.

# Adding the directory of the reaperml library to the path:
import sys
sys.path.insert(1, '/Users/macbook/Documents/BACKUP_GIT/reaperml/reaperml')

# Impoert the various modules:
import fluid_wrapper
import reathon
import scikit_wrapper
import utils

# Make the various modules available:
fluid = fluid_wrapper
reaper = reathon
ml = scikit_wrapper
ut = utils
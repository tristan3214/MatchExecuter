from __future__ import division, print_function, absolute_import

from MatchParam import MatchParam

"""
This runs through example code in using MatchParam.py.  This file is Python 3.x compatible.
"""

# Pass in MATCH parameter with 2 filters (1 CMD) with no zinc or background.
no_zinc_2filters_woback = MatchParam("no_zinc_2filters_woback.param")
no_zinc_2filters_woback.printKeys() # to see the keys for you instance use this
print()
print("Current values from the passed in parameter file:")
no_zinc_2filters_woback.print()
print()

# Changing basic values
no_zinc_2filters_woback.change("dAv", 0.1) # change from 0.2 to 0.1
print("The differential reddening has changed:")
no_zinc_2filters_woback.print()
print()

# Change the list of time bins need to specify my new start and end times
start = [6.6, 6.8, 7.0, 7.2]
end = [6.8, 7.0, 7.2, 7.4]
num = len(start)
no_zinc_2filters_woback.change("Ntbins", num)
no_zinc_2filters_woback.change("tstart", start)
no_zinc_2filters_woback.change("tend", end)
print("Changed time bins:")
no_zinc_2filters_woback.print()
print()

# Now maybe you want to add an excluded region.  These are rectangles consisting of a list of 8 numbers (1 point for each vertex).
exclude = [0.12, 25.4, 1.0, 25.4, 1.0, 27.0, 0.12, 27.0] # note this IS a rectangle
no_zinc_2filters_woback.change("Nexclude", 1)
no_zinc_2filters_woback.change("exclude", exclude)
print("Changed exclude bins:")
no_zinc_2filters_woback.print()
print()

# add a background
no_zinc_2filters_woback.change("lLine_1", -1)
no_zinc_2filters_woback.change("lLine_2", 5)
no_zinc_2filters_woback.change("scale", -1)
no_zinc_2filters_woback.change("background", "background.txt")
print("Notice some new keys at the bottom")
no_zinc_2filters_woback.printKeys()
print()
print("Now with background:")
no_zinc_2filters_woback.print()
print()

# save this new and edited parameter object
no_zinc_2filters_woback.save(name="editted_param.param") # saves in current working directory


# MatchParam can calculate the maxes and minimum mags that one normally has to calculate somewhere else.
# This takes time.  Given the photometry file I can find the brightest magnitudes, or given the fake stars I can find
# the 50% completeness for the dimmest magnitude. All one has to do is leave a string where there would be a number in the parameter
# file and I take care of the rest (see min_string.param and max_string.param in the examples file).

# Find the min or the brightest magnitude
findMinParam = MatchParam("min_string.param", photFile="photometry.phot")
print("Notice there are values where the strings used to be:")
findMinParam.print()
print()

# If you want to use the brightest in the optional background.
findMinParam = MatchParam("min_string.param", photFile="photometry.phot", useBackgroundMin=True)
print("Now those values are are different because of my background:")
findMinParam.print()
print()

# Find the max, or the dimmest magnitude using the 50% completeness.
findMaxParam = MatchParam("max_string.param", fakeFile="fake.fake")
print("Notice there are values where the max strings used to be:")
findMaxParam.print()
print()

# Of course you can do a combination of these two and you don't have to do it for all the specified filters.

# Other passed in parameter files

# Pass in MATCH parameter with 3 filters (2 CMDs) and references a background.
zinc_w_back = MatchParam("zinc_wback.param")
#zinc_w_back.print()
#zinc_w_back.printKeys()

# Pass in MATCH parameter with 3 filters (2 CMDs) and no background.
zinc_wo_back = MatchParam("zinc_woback.param")
#print()
#zinc_wo_back.print()
#print()
#zinc_wo_back.printKeys()
#print()

# To use ssp pass in an ssp-like parameter file and set the ssp parameter to True.

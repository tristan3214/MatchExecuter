#!/usr/bin/env python
from __future__ import print_function, division, absolute_import

import matplotlib.pyplot as plt
import seaborn
import sys
import os

from UsefulFunctions import SFH

zc = sys.argv[1]

name = zc.spit("/")[-1]

csf = SFH(zc, cumulative=True, bins=2, label="Test_%s" % name)

csf.calculateCSF()

#print(csf.getX())
#print(csf.getY())

plt.plot(csf.getX(), csf.getY())

#print(os.getcwd())

plt.savefig("/astro/users/tjhillis/M83/remnants/testExecuter/testCSF_%s.png" % name)

#!/usr/bin/env python
from __future__ import print_function, division

import sys

import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import seaborn

__author__ = "Tristan J. Hillis"

"""
This program uses a class to plot star formation rate (SFR) or star formation (SF) using the standard output files
from MATCH; either from "zcombine" or "zcmerge".  The user can specify command line arguments that point
to, potentially, multiple star formation history (SFH) files that will all be plotted on the same axes.  Otherwise, if
no command line arguements are specified, the user can manually point to the files of choice by editing this
program.
"""

def main():
    """
    Runs main program.
    """
    try:
        sys.argv[1]
        files = sys.argv[1:]
        SFHs = []
        for f in files:
            SFHs.append(SFH(f))
        plotAllSFR(SFHs)
    except IndexError:
        #fit_1 = SFH("../mount/remnants/testFakes/fit_1.zc", label="H026 fit & fake")
        #fit_2 = SFH("../mount/remnants/testFakes/fit_2.zc", label="H026 fit M067 fake")
        #fit_3 = SFH("../mount/remnants/testFakes/fit_3.zc", label="M067 fit & fake")
        #fit_4 = SFH("../mount/remnants/testFakes/fit_4.zc", label="M067 fit H026 fake")

        #fit_1 = SFH("../mount/remnants/testFakes/fit_5.zc", label="H026 fit & fake")
        #fit_2 = SFH("../mount/remnants/testFakes/fit_6.zc", label="H026 fit M067 fake")
        #fit_3 = SFH("../mount/remnants/testFakes/fit_7.zc", label="M067 fit & fake")
        #fit_4 = SFH("../mount/remnants/testFakes/fit_8.zc", label="M067 fit H026 fake")

        #fit_1 = SFH("../mount/remnants/testFakes/fit_11.zc", label="M143 fit & fake")
        #fit_2 = SFH("../mount/remnants/testFakes/fit_12.zc", label="M143 fit M153 fake")
        #fit_3 = SFH("../mount/remnants/testFakes/fit_13.zc", label="M153 fit & fake")
        #fit_4 = SFH("../mount/remnants/testFakes/fit_14.zc", label="M153 fit M143 fake")

        #fit_1 = SFH("../mount/remnants/testFakes/fit_1.zc", label="H026 fit & fake")
        #fit_2 = SFH("../mount/remnants/testFakes/fit_17.zc", label="H026 fit M048 fake")
        #fit_3 = SFH("../mount/remnants/testFakes/fit_15.zc", label="M048 fit & fake")
        #fit_4 = SFH("../mount/remnants/testFakes/fit_16.zc", label="M048 fit H026 fake")

        #fit_1 = SFH("../mount/remnants/testFakes/fit_19.zc", label="M177 fit & fake")
        #fit_2 = SFH("../mount/remnants/testFakes/fit_20.zc", label="M177 fit M046 fake")
        #fit_3 = SFH("../mount/remnants/testFakes/fit_21.zc", label="M046 fit & fake")
        #fit_4 = SFH("../mount/remnants/testFakes/fit_22.zc", label="M046 fit M177 fake")

        #fit_1 = SFH("../mount/remnants/testFakes/fit_23.zc", label="M181 fit & fake", bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes/fit_25.zc", label="M181 fit M133 fake", bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes/fit_24.zc", label="M133 fit & fake", bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes/fit_26.zc", label="M133 fit M188 fake", bins=12)

        #fit_1 = SFH("../mount/remnants/testFakes/fit_27.zc", label="M168 fit & fake")
        #fit_2 = SFH("../mount/remnants/testFakes/fit_29.zc", label="M168 fit M322 fake")
        #fit_3 = SFH("../mount/remnants/testFakes/fit_28.zc", label="M322 fit & fake")
        #fit_4 = SFH("../mount/remnants/testFakes/fit_30.zc", label="M322 fit M168 fake")

        #fit_1 = SFH("../mount/remnants/testFakes/fit_039.zc", label="M204 fit & fake", bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes/fit_040.zc", label="M204 fit M180 fake", bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes/fit_041.zc", label="M180 fit & fake", bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes/fit_042.zc", label="M180 fit M204 fake", bins=12)

        
        #plotAllSFR(SFH_list=[fit_1, fit_2, fit_3, fit_4], startLineWidth=4.0, legendLoc=1)

        ##### Cumulative SF (set bins=12 for first ~60 million years)
        
        #fit_1 = SFH("../mount/remnants/testFakes/fit_23.zc", label="M181 fit & fake", cumulative=True, bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes/fit_25.zc", label="M181 fit M133 fake", cumulative=True, bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes/fit_24.zc", label="M133 fit & fake", cumulative=True, bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes/fit_26.zc", label="M133 fit M188 fake", cumulative=True, bins=12)

        #fit_1 = SFH("../mount/remnants/testFakes/fit_035.zc", label="M168 fit & fake", cumulative=True, bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes/fit_036.zc", label="M168 fit M322 fake", cumulative=True, bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes/fit_037.zc", label="M322 fit and fake", cumulative=True, bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes/fit_038.zc", label="M322 fit M168 fake", cumulative=True, bins=12)

        #fit_1 = SFH("../mount/remnants/testFakes/fit_051.zc", label="M177 fit & fake", cumulative=True, bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes/fit_052.zc", label="M177 fit M159 fake", cumulative=True, bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes/fit_053.zc", label="M159 fit & fake", cumulative=True, bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes/fit_054.zc", label="M159 fit M177 fake", cumulative=True, bins=12)

        #fit_1 = SFH("../mount/remnants/testFakes/fit_043.zc", label="M128 fit & fake", cumulative=True, bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes/fit_044.zc", label="M128 fit M084 fake", cumulative=True, bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes/fit_045.zc", label="M084 fit & fake", cumulative=True, bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes/fit_046.zc", label="M084 fit M128 fake", cumulative=True, bins=12)

        #fit_1 = SFH("../mount/remnants/testFakes/fit_047.zc", label="H026 fit & fake", cumulative=True, bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes/fit_048.zc", label="M048 fit & fake", cumulative=True, bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes/fit_049.zc", label="H026 fit M048 fake", cumulative=True, bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes/fit_051.zc", label="M048 fit H026 fake", cumulative=True, bins=12)

        #fit_1 = SFH("../mount/remnants/testFakes/fit_055.zc", label="M202 fit & fake", cumulative=True, bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes/fit_056.zc", label="M202 fit M048 fake", cumulative=True, bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes/fit_057.zc", label="M048 fit & fake", cumulative=True, bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes/fit_058.zc", label="M048 fit M202 fake", cumulative=True, bins=12)

        #fit_1 = SFH("../mount/remnants/testFakes/fit_059.zc", label="M057 fit & fake", cumulative=True, bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes/fit_060.zc", label="M057 fit M180 fake", cumulative=True, bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes/fit_061.zc", label="M180 fit & fake", cumulative=True, bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes/fit_062.zc", label="M180 fit M057 fake", cumulative=True, bins=12)

        #fit_1 = SFH("../mount/remnants/testFakes/fit_039.zc", label="M204 fit & fake", cumulative=True, bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes/fit_040.zc", label="M204 fit M180 fake", cumulative=True, bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes/fit_041.zc", label="M180 fit & fake", cumulative=True, bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes/fit_042.zc", label="M180 fit M204 fake", cumulative=True, bins=12)


        #fit_1 = SFH("../mount/remnants/testFakes/fit_063.zc", label="M084 fit & fake", cumulative=True, bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes/fit_064.zc", label="M084 fit H139 fake", cumulative=True, bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes/fit_065.zc", label="H139 fit & fake", cumulative=True, bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes/fit_066.zc", label="H139 fit M084 fake", cumulative=True, bins=12)

        #fit_1 = SFH("../mount/remnants/testFakes/fit_067.zc", label="M128 fit & fake", cumulative=True, bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes/fit_068.zc", label="M128 fit H139 fake", cumulative=True, bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes/fit_069.zc", label="H139 fit & fake", cumulative=True, bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes/fit_070.zc", label="H139 fit M128 fake", cumulative=True, bins=12)

        #fit_1 = SFH("../mount/remnants/testFakes/fit_071.zc", label="M128 fit & fake", cumulative=True, bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes/fit_072.zc", label="M128 fit M093 fake", cumulative=True, bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes/fit_073.zc", label="M093 fit & fake", cumulative=True, bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes/fit_074.zc", label="M093 fit M128 fake", cumulative=True, bins=12)

        #fit_1 = SFH("../mount/remnants/testFakes/fit_075.zc", label="M128 fit & fake", cumulative=True, bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes/fit_076.zc", label="M128 fit M179 fake", cumulative=True, bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes/fit_077.zc", label="M179 fit & fake", cumulative=True, bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes/fit_078.zc", label="M179 fit M128 fake", cumulative=True, bins=12)

        #fit_1 = SFH("../mount/remnants/testFakes/fit_079.zc", label="M128 fit & fake", cumulative=True, bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes/fit_080.zc", label="M128 fit M151 fake", cumulative=True, bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes/fit_081.zc", label="M151 fit & fake", cumulative=True, bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes/fit_082.zc", label="M151 fit M128 fake", cumulative=True, bins=12)

        #fit_1 = SFH("../mount/remnants/testFakes/fit_083.zc", label="M048 fit & fake", cumulative=True, bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes/fit_084.zc", label="M048 fit M023 fake", cumulative=True, bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes/fit_085.zc", label="M023 fit & fake", cumulative=True, bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes/fit_086.zc", label="M023 fit M048 fake", cumulative=True, bins=12)

        #fit_1 = SFH("../mount/remnants/testFakes/fit_087.zc", label="M048 fit & fake", cumulative=True, bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes/fit_088.zc", label="M048 fit M093 fake", cumulative=True, bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes/fit_089.zc", label="M093 fit & fake", cumulative=True, bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes/fit_090.zc", label="M093 fit M048 fake", cumulative=True, bins=12)

        #fit_1 = SFH("../mount/remnants/testFakes/fit_091.zc", label="M048 fit & fake", cumulative=True, bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes/fit_092.zc", label="M048 fit H193 fake", cumulative=True, bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes/fit_093.zc", label="H139 fit & fake", cumulative=True, bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes/fit_094.zc", label="H139 fit M048 fake", cumulative=True, bins=12)

        #fit_1 = SFH("../mount/remnants/testFakes/fit_095.zc", label="M048 fit & fake", cumulative=True, bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes/fit_096.zc", label="M048 fit M322 fake", cumulative=True, bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes/fit_097.zc", label="M322 fit & fake", cumulative=True, bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes/fit_098.zc", label="M322 fit M048 fake", cumulative=True, bins=12)
        """
        # Tests with updated 50% completeness calculations
        fit_1 = SFH("../mount/remnants/testFakes2/fit_M048_withM048fake.zc", label="M048 fit & fake", cumulative=True, bins=12)
        fit_2 = SFH("../mount/remnants/testFakes2/fit_M048_withM023.zc", label="M048 fit M023 fake", cumulative=True, bins=12)
        fit_3 = SFH("../mount/remnants/testFakes2/fit_M023_withM023.zc", label="M023 fit & fake", cumulative=True, bins=12)
        fit_4 = SFH("../mount/remnants/testFakes2/fit_M023_withM048.zc", label="M023 fit M048 fake", cumulative=True, bins=12)

        fit_1 = SFH("../mount/remnants/testFakes2/fit_M048_withM048fake.zc", label="M048 fit & fake", cumulative=True, bins=12)
        fit_2 = SFH("../mount/remnants/testFakes2/fit_M048_withM093.zc", label="M048 fit M093 fake", cumulative=True, bins=12)
        fit_3 = SFH("../mount/remnants/testFakes2/fit_M093_withM093.zc", label="M093 fit & fake", cumulative=True, bins=12)
        fit_4 = SFH("../mount/remnants/testFakes2/fit_M093_withM048.zc", label="M093 fit M048 fake", cumulative=True, bins=12)
        """
        # No SF in M057
        #fit_1 = SFH("../mount/remnants/testFakes2/fit_M057_withM057.zc", label="M057 fit & fake", cumulative=True, bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes2/fit_M057_withM195a.zc", label="M057 fit M195a fake", cumulative=True, bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes2/fit_M195a_withM195a.zc", label="M195a fit & fake", cumulative=True, bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes2/fit_M195a_withM057.zc", label="M195a fit M057 fake", cumulative=True, bins=12)

        # No SF in M057
        #fit_1 = SFH("../mount/remnants/testFakes2/fit_M057_withM057.zc", label="M057 fit & fake", cumulative=True, bins=12)
        #fit_2 = SFH("../mount/remnants/testFakes2/fit_M057_withM084.zc", label="M057 fit M084 fake", cumulative=True, bins=12)
        #fit_3 = SFH("../mount/remnants/testFakes2/fit_M084_withM084.zc", label="M084 fit & fake", cumulative=True, bins=12)
        #fit_4 = SFH("../mount/remnants/testFakes2/fit_M084_withM057.zc", label="M084 fit M057 fake", cumulative=True, bins=12)
 
        #plotAllCSF(SFH_list=[fit_1, fit_2, fit_3, fit_4], startLineWidth=4.0)

        """
        # ["M073", "H026", "H035", "M135", "H142", "M187", "M093", "H107", "M168"]
        fit_1 = SFH("../mount/remnants/comprehensiveTest/fit_M073_usingM073.zc", cumulative=True, bins=12)
        fit_2 = SFH("../mount/remnants/comprehensiveTest/fit_M073_usingH026.zc", cumulative=True, bins=12)
        fit_3 = SFH("../mount/remnants/comprehensiveTest/fit_M073_usingH035.zc", cumulative=True, bins=12)
        fit_4 = SFH("../mount/remnants/comprehensiveTest/fit_M073_usingM135.zc", cumulative=True, bins=12)
        fit_5 = SFH("../mount/remnants/comprehensiveTest/fit_M073_usingH142.zc", cumulative=True, bins=12)
        fit_6 = SFH("../mount/remnants/comprehensiveTest/fit_M073_usingM187.zc", cumulative=True, bins=12)
        fit_7 = SFH("../mount/remnants/comprehensiveTest/fit_M073_usingM093.zc", cumulative=True, bins=12)
        fit_8 = SFH("../mount/remnants/comprehensiveTest/fit_M073_usingH107.zc", cumulative=True, bins=12)
        fit_9 = SFH("../mount/remnants/comprehensiveTest/fit_M073_usingM168.zc", cumulative=True, bins=12)

        plotAllCSF(SFH_list=[fit_1, fit_2, fit_3, fit_4, fit_5, fit_6, fit_7, fit_8, fit_9], startLineWidth=4.0)
        """
        """
        #["M204", "H132", "M084", "M168", "H139", "M093", "M175"]
        fit_1 = SFH("../mount/remnants/comprehensiveTest/fit_M204_usingM204.zc", cumulative=True, bins=12)
        fit_2 = SFH("../mount/remnants/comprehensiveTest/fit_M204_usingH132.zc", cumulative=True, bins=12)
        fit_3 = SFH("../mount/remnants/comprehensiveTest/fit_M204_usingM084.zc", cumulative=True, bins=12)
        fit_4 = SFH("../mount/remnants/comprehensiveTest/fit_M204_usingM168.zc", cumulative=True, bins=12)
        fit_5 = SFH("../mount/remnants/comprehensiveTest/fit_M204_usingH139.zc", cumulative=True, bins=12)
        fit_6 = SFH("../mount/remnants/comprehensiveTest/fit_M204_usingM093.zc", cumulative=True, bins=12)
        fit_7 = SFH("../mount/remnants/comprehensiveTest/fit_M204_usingM175.zc", cumulative=True, bins=12)

        plotAllCSF(SFH_list=[fit_1, fit_2, fit_3, fit_4, fit_5, fit_6, fit_7], startLineWidth=4.0)
        """

        # ["M174a", "M023", "H069", "H107", "M143", "M048", "M322"]        
        # factor [1.        ,  1.06275549,  1.4895832 ,  0.53124991,  0.66666661, 2.06249983,  0.37499994]
        """
        fit_1 = SFH("../mount/remnants/comprehensiveTest/fit_M174a_usingM174a.zc", cumulative=True, bins=11, label="6.090113:1x M174a")
        fit_2 = SFH("../mount/remnants/comprehensiveTest/fit_M174a_usingM023.zc", cumulative=True, bins=11, label="1.063x M023")
        fit_3 = SFH("../mount/remnants/comprehensiveTest/fit_M174a_usingH069.zc", cumulative=True, bins=11, label="1.49x H069")
        fit_4 = SFH("../mount/remnants/comprehensiveTest/fit_M174a_usingH107.zc", cumulative=True, bins=11, label="0.53x H107")
        fit_5 = SFH("../mount/remnants/comprehensiveTest/fit_M174a_usingM143.zc", cumulative=True, bins=11, label="0.67x M143")
        fit_6 = SFH("../mount/remnants/comprehensiveTest/fit_M174a_usingM048.zc", cumulative=True, bins=11, label="2.06x M048")
        fit_7 = SFH("../mount/remnants/comprehensiveTest/fit_M174a_usingM322.zc", cumulative=True, bins=11, label="0.37x M322")
        """
        """
        fit_1 = SFH("../mount/remnants/comprehensiveTest/fit_M174a_usingM174a_fix.zc", cumulative=True, bins=11, label="6.090113:1x M174a")
        fit_2 = SFH("../mount/remnants/comprehensiveTest/fit_M174a_usingM023_fix.zc", cumulative=True, bins=11, label="1.063x M023")
        fit_3 = SFH("../mount/remnants/comprehensiveTest/fit_M174a_usingH069_fix.zc", cumulative=True, bins=11, label="1.49x H069")
        fit_4 = SFH("../mount/remnants/comprehensiveTest/fit_M174a_usingH107_fix.zc", cumulative=True, bins=11, label="0.53x H107")
        fit_5 = SFH("../mount/remnants/comprehensiveTest/fit_M174a_usingM143_fix.zc", cumulative=True, bins=11, label="0.67x M143")
        fit_6 = SFH("../mount/remnants/comprehensiveTest/fit_M174a_usingM048_fix.zc", cumulative=True, bins=11, label="2.06x M048")
        fit_7 = SFH("../mount/remnants/comprehensiveTest/fit_M174a_usingM322_fix.zc", cumulative=True, bins=11, label="0.37x M322")
        """

        #plotAllCSF(SFH_list=[fit_1, fit_2, fit_3, fit_4, fit_5, fit_6, fit_7], startLineWidth=4.0)



def plotAllSFR(SFH_list, startLineWidth=3.0, endLineWidth=0.0, legendLoc=1):
    """
    Takes a list of SFH objects and plots all the SFR on one axis.
    """
    lineWidthStep = (startLineWidth - endLineWidth) / len(SFH_list)
    lineWidth = startLineWidth
    legend = False
    counter = 0
    for sfh in SFH_list:
        sfh.calculateSFR()
        if sfh.getLabel() is not None:
            legend = True
            plt.plot(sfh.getX(), sfh.getY(), linewidth=lineWidth, label=sfh.getLabel(), zorder=counter)
        else:
            plt.plot(sfh.getX(), sfh.getY(), linewidth=lineWidth, zorder=counter)

        spot, SFR, plus, minus = sfh.getErrors()
        plt.errorbar(spot, SFR, yerr=SFR*0.1, linestyle='none', fillstyle='none', capsize=0, linewidth=1.2, color='k',zorder=10)
        if sfh.isErrors():
            spot, SFR, plus, minus = sfh.getErrors()
            plt.errorbar(spot, SFR, yerr=[minus.tolist(), plus.tolist()], linestyle='none', fillstyle='none',
                         color='k', capsize=0, linewidth=1.2)

        lineWidth -= lineWidthStep
        counter += 1

    plt.ylabel(r"SFR ($M_\odot$ / yr)")
    plt.xlabel("Time (Myrs)")
    #plt.yscale('log')
    if legend:
        plt.legend(loc=legendLoc)

    plt.show()

def plotAllSF(SFH_list, startLineWidth=3.0, endLineWidth=0.5):
    """
    Takes a list of SFH objects and plot all the SF on one axis
    """
    lineWidthStep = (startLineWidth - endLineWidth) / len(SFH_list)
    lineWidth = startLineWidth
    legend = False
    for sfh in SFH_list:
        sfh.calculateSF()
        if sfh.getLabel() is not None:
            legend = True
            plt.plot(sfh.getX(), sfh.getY(), linewidth=lineWidth, label=sfh.getLabel())
        else:
            plt.plot(sfh.getX(), sfh.getY(), linewidth=lineWidth)

        if sfh.isErrors():
            spot, SF, plus, minus = sfh.getErrors()
            plt.errorbar(spot, SF, yerr=[minus.tolist(), plus.tolist()], linestyle='none', fillstyle='none',
                         color='k', capsize=0, linewidth=1.2)

        lineWidth -= lineWidthStep

    plt.ylabel(r"SF ($M_\odot$)")
    plt.xlabel("Time (Myrs)")
    if legend:
        plt.legend()

    plt.show()

def plotAllCSF(SFH_list, startLineWidth=3.0, endLineWidth=0.5):
    """
    Takes passed in list of SFH objects and plots them for cumulative SF.
    """
    lineWidthStep = (startLineWidth - endLineWidth) / len(SFH_list)
    lineWidth = startLineWidth
    legend = False
    for sfh in SFH_list:
        sfh.calculateCSF()
        print(sfh.getY())
        if sfh.getLabel() is not None:
            legend = True
            plt.plot(sfh.getX(), sfh.getY(), linewidth=lineWidth, label=sfh.getLabel())
        else:
            plt.plot(sfh.getX(), sfh.getY(), linewidth=lineWidth)

        if sfh.isErrors():
            spot, SF, plus, minus = sfh.getErrors()
            plt.errorbar(spot, SF, yerr=[minus.tolist(), plus.tolist()], linestyle='none', fillstyle='none',
                         color='k', capsize=0, linewidth=1.2)

        lineWidth -= lineWidthStep

    plt.ylim([0.0, 1.0])
    plt.ylabel(r"Cumulative Stellar Mass")
    plt.xlabel("Time (Myrs)")
    if legend:
        plt.legend()

    plt.show()

    pass


class SFH(object):
    """
    This class instantiates being able to plot a SFH by ultimately returning the x and y for the plot.
    """

    def __init__(self, SFH, zcmerge=False, SFR=True, bins=17, label=None, cumulative=False):
        # Initial variables
        self._file = SFH
        self._zcmerge = zcmerge  # Tells program if zcmerge/zcombine was used; default is zcombine
        self._SFR = SFR  # Tells program which quantity to plot on y-axis.  Default is SFR
        self._bins = bins
        self._label = label
        self._cumulative = cumulative # allows the user to specify they want cumulative SF calculated for their SFH

        self._x = None  # Variable that will later hold the time value.
        self._y = None  # Variable that will later hold the SF/SFR value

    def calculateSFR(self):
        """
        Calculates the SFR for the SFH and returns the x and y for plotting by user.
        """
        To, Tf, SFR, plusError, minusError = self._extractData()
        if self._bins > To.size:
            print("The number of bins specified is larger than the number found in the file.")
            sys.exit(1)

        timeStep = 10**Tf - 10**To  # This is the step of each bin in linear time
        To_linear = 10**To
        Tf_linear = 10**Tf
        SF = SFR * timeStep

        timePlot = []
        sfrPlot = []
        for i in range(self._bins):
            # add the first one
            timePlot.append(To_linear[i])
            sfrPlot.append(SFR[i])

            # add the second one
            timePlot.append(Tf_linear[i])
            sfrPlot.append(SFR[i])
        timePlot = np.asarray(timePlot)
        sfrPlot = np.asarray(sfrPlot)
            
        print("SF for the past %.1f million years (solar mass)" % (np.sum(SF[:self._bins]) / 10**6))

        self._x = timePlot / 10**6 
        self._y = sfrPlot

    def calculateSF(self):
        """
        Calculates the SF for the SFH and returns the x and y for plotting by user.
        """
        To, Tf, SFR, plusError, minusError = self._extractData()
        if To.size > self._bins:
            print("The number of bins specified is larger than the number found in the file.")
            sys.exit(1)

        timeStep = 10**Tf - 10**To  # This is the step of each bin in linear time
        To_linear = 10**To
        Tf_linear = 10**Tf
        SF = SFR * timeStep

        timePlot = []
        sfPlot = []
        for i in range(self._bins):
            # add the first one
            timePlot.append(To_linear[i])
            sfPlot.append(SF[i])

            # add the second one
            timePlot.append(Tf_linear[i])
            sfPlot.append(SF[i])

        print("SF for the past %.1f million years (solar mass)" % (np.sum(SF[:self._bins]) / 10**6))

        self._x = timePlot / 10**6
        self._y = sfPlot

    def calculateCSF(self):
        """
        This will calculate the cumulative star formation history for the specified number of bins.
        The plot goes from "100%" down to "0%" with increasing time.
        """
        To, Tf, SFR, plusError, minusError = self._extractData()

        if len(To) == 1:
            To, Tf, SFR, plusError, minusError = np.array([To]), np.array([Tf]), np.array([SFR]), np.array([plusError]), np.array([minusError])
            #print(SFR, type(SFR))
        
        To_linear = 10**To
        Tf_linear = 10**Tf
        timeStep = Tf_linear - To_linear

        SF = SFR * timeStep
        SF = SF[:self._bins] # grabs the specified bins to calculate CSF for

        timeStep = timeStep[:self._bins]
        #timeElapsed = np.cumsum(timeStep[:self._bins])
        timeElapsed = To_linear[:self._bins]

        timePlot = np.insert(Tf_linear[:self._bins], 0, To_linear[0])
        SF = np.insert(SF, 0, 0)
        
        totSF = np.sum(SF)
        cumSum = np.cumsum(SF)
        cumSumFrac = 1 - (cumSum / totSF)

        #print(To[:self._bins])
        #print(Tf[:self._bins])
        #print(SF)
        #print(totSF)
        #print(cumSum)
        #print(cumSumFrac)
        #print(np.cumsum(SF[::-1]))
        #print(1-(np.cumsum(SF[::-1]) / totSF))
        
        self._x = timePlot /  10**6
        self._y = cumSumFrac
        #print("X:", self._x)
        #print("Y:", self._y)
        #print()

    def getErrors(self):
        """
        Retrieves the errors of the SFH
        """
        To, Tf, SFR, plusError, minusError = self._extractData()

        To_linear = 10**To
        Tf_linear = 10**Tf
        timeStep = Tf_linear - To_linear

        errorSpots = (To_linear + (timeStep / 2.0)) / 10**6

        if self._SFR:
            return [errorSpots[:self._bins], SFR[:self._bins], plusError[:self._bins], minusError[:self._bins]]
        else:
            return [errorSpots[:self._bins], SFR[:self._bins]*timeStep[:self._bins],
                    plusError*timeStep[:self._bins], minusError*timeStep[:self._bins]]

    def getLabel(self):
        """
        Retrieves the string used for a legend.
        """
        return self._label

    def getX(self):
        """
        Returns x-axis
        """
        return self._x

    def getY(self):
        """
        Returns y-axis
        """
        return self._y

    def isErrors(self):
        """
        Returns which file type is used from MATCH (i.e. zcombine or zcmerge)
        """
        return self._zcmerge

    def _extractData(self):
        """
        Opens passed in file and extracts data from it and returns it.
        """
        To, Tf, SFR, plusError, minusError = None, None, None, None, None
        if self._zcmerge:
            To, Tf, SFR, plusError, minusError = np.loadtxt(self._file, usecols=[0, 1, 3, 4, 5], unpack=True)
        else:
            To, Tf, SFR, plusError, minusError = np.genfromtxt(self._file, usecols=[0, 1, 3, 4, 5], skip_header=6,
                                                               skip_footer=1, unpack=True)
        return [To, Tf, SFR, plusError, minusError]


if __name__ == "__main__":
    main()

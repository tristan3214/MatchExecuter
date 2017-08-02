#!/usr/bin/env python2
from __future__ import print_function, division, absolute_import

import numpy as np
import pandas as pd
from astropy.wcs import WCS
import pointCross
import sys

"""
Creates a function that takes two files. one being the density for all the current fakes that have been run and the other being a 
list of all the fake stars.  It will compare them and find the best fake list to use for calcsfh in each fit run.
"""

def matchDensities(threshold, fakes, densities):
    """
    Passed in parameters are assumed to be Pandas DataFrames with two columns.  The first column
    is "id" and the second is "density".  The threshold defines some factor that the density can be within to be "matched"
    Returns a Pandas DataFrame with the SNR id as column "id" and its correspondingly matched density's id as "match".
    It is possible to have None as a matched density, which corresponds to the SNR's density being outside the threshold
    to be considered matched.
    """
    
    matched = []
    unique = set()
    count = 0
    run_count = 0
    for i, curr_id in enumerate(densities['id']):
        # calculate and minimize a distance from this current density to all the "fake" ones
        curr_dens = densities['density'][i]
        factor = []
        for j, fake_id in enumerate(fakes['id']):
            fake_dens = fakes['density'][j]
            curr_factor = None
            #if curr_id == "M181":
            #    print("DENSITY (%s):" % (fakes['id'][j]), fake_dens, curr_dens) 
            if fake_dens <= curr_dens:
                curr_factor = curr_dens / fake_dens
            else:
                curr_factor = fake_dens / curr_dens
            
            factor.append(curr_factor)
        #if curr_id == "M181":
        #    print(factor)
        idx = np.argmin(factor)
        min_factor = factor[idx]

        if min_factor <= threshold:
            #print(curr_id, fakes['id'][idx])
            if str(curr_id) == str(fakes['id'][idx]):
                count += 1
            matched.append(fakes['id'][idx])
            #print(i+1, curr_id, fakes['id'][idx])
            unique.add(fakes['id'][idx])
            run_count += 1
        else:
            matched.append(None)
            #print(i+1, curr_id, None)

    #print("Number of snrs matched to a relative density:", run_count)
    data = pd.DataFrame({"id":densities['id'].values, "match":matched})
    #print(data)
    #print(unique, len(unique))
    #print(count)

    return data

def getDAv(path, fitName):
    """
    Takes in a path to where a standard best_dAvs.ls file is held and uses the fitName to extract the best dAv and Av.
    Returns these values as a tuple as (dAv, Av) else if the fitname is not found returns none.
    """
    name, dAv, Av = np.genfromtxt(path+"best_dAvs.ls", usecols=[0,1,2], unpack=True, dtype=str)
    if name.size == 1:
        name = np.array([name])
        dAv = np.array([dAv])
        Av = np.array([Av])
        
    if fitName not in name:
        return None
    else:
        idx = np.where(name == fitName)[0][-1]
        return (dAv[idx], Av[idx])
def getMass(path, fitNames, massname, skiprows=0):
    """
    Takes in a path to where a standard best_dAvs.ls file is held and uses the fitName to extract mass for the best fit.
    Returns these values as a tuple as (50th, 84th, 16th) else if the fitname is not found returns none. Returns are strings.
    """
    name, mass, plus, minus = np.genfromtxt(path+massname, usecols=[0,1,2,3], unpack=True, dtype=str, skip_header=skiprows)
    for fitName in fitNames:
        if name.size == 1:
            name = np.array([name])
            mass = np.array([mass])
            plus = np.array([plus])
            minus = np.array([minus])

        if fitName not in name:
            continue
        else:
            idx = np.where(name == fitName)[0][-1]
            return (mass[idx], plus[idx], minus[idx])
    return None

    
def getShiftedSNRFK5(snr):
    """
    Pass in an snr id and then return the shifted RA and DEC coordinates using x_off and y_off in the master list.
    """
    # Read in master list
    master = pd.read_csv("/home/tristan/BenResearch/M83/code/textFiles/master_list.txt")

    # available fields
    fitsFiles = ["12513_MESSIER-083","12513_MESSIER-083-POS2","12513_M83-F3","12513_M83-F4","12513_M83-F5","12513_M83-F6","12513_M83-F7"] # fields [1, 2, 3, 4, 5, 6, 7]

    # get index of the passed in snr
    idx = np.where(snr == master['id'].values)[0][0]
    # get coordinates as well as x_off and y_off
    ra, dec, x_off, y_off, field = master['ra'][idx], master['dec'][idx], master['x_off'][idx], master['y_off'][idx], master['field'][idx]

    # make wcs
    w = WCS("/home/tristan/BenResearch/M83/fields/%s/%s_F438W_drz.chip1.fits"%(fitsFiles[int(field) - 1], fitsFiles[int(field) - 1]))

    world = np.array([[ra, dec]], np.float_)
    pixcrd = w.wcs_world2pix(world, 0)
    newPixcrd = np.array([[pixcrd[0][0]+x_off, pixcrd[0][1]+y_off]], np.float_)
    newWorld = w.wcs_pix2world(newPixcrd, 0)

    # sample ras and decs with resolution of ~100 points
    c = (newWorld[0][0], newWorld[0][1])

    return c

def getSNRCircle(ra, dec, radius):
    """
    Pass in an ra, dec, and radius and this will return a Polygon that forms a circle in ra and decs
    """
    rads = np.linspace(0, 2*np.pi, 200)
    r = radius
    c = (ra, dec)
    points = []
    for j in range(len(rads)):
        points.append((_sample_x_circle(c, r, rads[j]), _sample_y_circle(c, r, rads[j])))
    circle = pointCross.Polygon(points)

    
def _sample_x_circle(c, r, rad):
    return c[0] + r*np.cos(rad)  / np.cos(np.radians(c[1])) # correct delta ra by a division of cosine of the declination

def _sample_y_circle(c, r, rad):
    return c[1] + r*np.sin(rad)


#### Start useful classes
class SFH(object):
    """
    This class instantiates being able to plot a SFH by ultimately returning the x and y for the plot.
    """

    def __init__(self, SFH, zcmerge=False, SFR=True, bins=17, label=None, cumulative=False):
        # Initial variables
        self._file = SFH
        self._zcmerge = zcmerge  # Tells program if zcmerge/zcombine was used; default is zcombine
        self._SFR = SFR  # Tells program which quantity to plot on y-axis.  Default is SFR
        self._bins = int(bins)
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

        if np.isnan(np.min(np.asarray(cumSumFrac))):
            cumSumFrac = np.linspace(0, 0, len(cumSumFrac))
        print(cumSumFrac)
        
        self._x = timePlot /  10**6
        self._y = cumSumFrac

    def getErrors(self):
        """
        Retrieves the errors of the SFH and returns a list with where the errors should be plotted along with the plus and 
        minus errors as [xErrorSpots, yErrorSpots, plusError, minusError].

        CSF Errors:  These errors are calculated with a simulation about a standard-normal distribution.  What is returned
        is the time over the calculated errors with the plus and minus CSF that can be plotted but is suggested to use fill between.
        Also returned is the 50th percentile time of the original CSF with the 50th percentiles of the plus and minus CSF representing
        the plus and minus errors in time.

        Suggested way to plot CSF errors: plt.fill_between(time, plus, minus, color='0.5', alpha=0.5)
        """
        To, Tf, SFR, plusError, minusError = self._extractData()

        # Make linear time step
        To_linear = 10**To
        Tf_linear = 10**Tf
        timeStep = Tf_linear - To_linear
        
        # errors are different when it is not a cumulative star formation plot
        if not self._cumulative:
            errorSpots = (To_linear + (timeStep / 2.0)) / 10**6

            if self._SFR:
                return [errorSpots[:self._bins], SFR[:self._bins], plusError[:self._bins], minusError[:self._bins]]
            else:
                return [errorSpots[:self._bins], SFR[:self._bins]*timeStep[:self._bins],
                        plusError*timeStep[:self._bins], minusError*timeStep[:self._bins]]
        else: # errors and error locations for cumulative star formation plot
            # generate 1000 Gaussian numbers for each bin time bin
            rands = [np.random.randn(1000) for i in range(To.size)]

            # multiply these gaussian numbers by either plus error or minus error depending on if the randum number is +/-
            gaussianError = [np.asarray([currRand*plusError[i] if currRand >= 0 else currRand*minusError[i] for currRand in rand]) for i,rand in enumerate(rands)]

            # add all these numbers to the original SFR and if the SFR is less than zero then set it to 0.
            SFRsimulation = [gaussian + SFR[i] for i,gaussian in enumerate(gaussianError)]
            SFRsimulation = [np.clip(sim, 0, np.inf, out=sim) for sim in SFRsimulation] # set any negative numbers to zero.         
            # Make SFRsimulation 1000 arrays of length 49 rather than 49 arrays of length 1000
            newSFRsimulation = []
            for i in xrange(1000):
                SFR_array = np.array([])
                for j, time_bin in enumerate(SFRsimulation):
                    SFR_array = np.append(SFR_array, time_bin[i])

                newSFRsimulation.append(SFR_array)
            SFRsimulation = newSFRsimulation

            # Change the SFR simulation to SF simulation
            SFsimulation = [timeStep*sim for sim in SFRsimulation]
            totals = [sim[:self._bins].sum() for sim in SFsimulation]
            
            # find the cumulative mass for only the bins we need
            cumSF_simulation = [np.cumsum(np.insert(currSF[:self._bins], 0, 0)) for currSF in SFsimulation]
            #print(cumSF_simulation)

            # calculate the cumulative stellar fraction for all 1000 trials
            csf_simulation = [(1 - (curr_cumSF / totals[i])) for i, curr_cumSF in enumerate(cumSF_simulation)]

            # Now with the 1000 cumulative stellar fractions we want to find the 84th, 50th, and 16th percentile for each time bin. First
            # we need to change the simulation to 1000 values per time bin rather than 1000 arrays of each a total SFH.
            reverseCSF_sim = []
            for i in xrange(len(csf_simulation[0])):
                time_bin = np.array([])
                for j in xrange(len(csf_simulation)):
                    time_bin = np.append(time_bin, csf_simulation[j][i])
                reverseCSF_sim.append(time_bin)
            csf_simulation = reverseCSF_sim

            # At this point one will have 1000 different CSF that could be plotted as 1000 different 1000 cumulative starformation plots.
            # Take the 84th and 16th percentile for each CSF and this will be the +/- error basis for the cumulative starformation plot.
            plus_csf = np.asarray([np.percentile(sim, 84) for sim in csf_simulation])
            fiftyth_csf = np.asarray([np.percentile(sim, 50) for sim in csf_simulation])
            minus_csf = np.asarray([np.percentile(sim, 16) for sim in csf_simulation])            
            
            timePlot = np.insert(Tf_linear[:self._bins], 0, To_linear[0])

            # Now that we have calculated the plus_csf and minus_csf we need to return two arrays that will be filled in between.
            # However, in some cases the minus might be above the original and the plus might below the original.  In these edge
            # cases we simply replace that CSF value with the original.
            original = self.getY() # original CSF values
            
            plus_csf = np.asarray([plus if plus > original[i] else original[i] for i, plus in enumerate(plus_csf)])
            minus_csf = np.asarray([minus if minus < original[i] else original[i] for i, minus in enumerate(minus_csf)])

            #print(plus_csf, minus_csf)
            
            # calculate the plus error and minus error in time based off
            original_time = self._interpolate(0.50, self.getX(), self.getY())
            minus_time = self._interpolate(0.50, self.getX(), minus_csf)
            plus_time = self._interpolate(0.50, self.getX(), plus_csf)

            return [timePlot / 10**6, plus_csf, minus_csf, (original_time, plus_time, minus_time)]
            
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
            To, Tf, SFR, plusError, minusError = np.loadtxt(self._file, usecols=[0, 1, 3, 4, 5], unpack=True, skiprows=1)
        else:
            To, Tf, SFR, plusError, minusError = np.genfromtxt(self._file, usecols=[0, 1, 3, 4, 5], skip_header=6,
                                                               skip_footer=1, unpack=True)
        return [To, Tf, SFR, plusError, minusError]

    def _interpolate(self, interpVals, x, y):
        """
        Returns the interpereted x value about the passed in interpVal(s).
        """
        linear = lambda y: (y-b) / m
        try:
            if type(interpVals) != list:
                idx1 = np.where(y >= interpVals)[0][-1] # get the upper value
                idx2 = np.where(y <= interpVals)[0][0] # get the lower value

                x1 = x[idx1]
                y1 = y[idx1]

                x2 = x[idx2]
                y2 = y[idx2]

                m = (y2 - y1) / (x2 - x1)
                b = (-m * x1 + y1)
                return linear(interpVals)
            else:
                list_of_interps = []
                for interp in interpVals:
                    idx1 = np.where(y >= interp)[0][-1] # get the upper value
                    idx2 = np.where(y <= interp)[0][0] # get the lower value

                    x1 = x[idx1]
                    y1 = y[idx1]

                    x2 = x[idx2]
                    y2 = y[idx2]

                    m = (y2 - y1) / (x2 - x1)
                    b = (-m * x1 + y1)
                    list_of_interps.append(linear(interp))
                return list_of_interps
        except IndexError: # If there is a misses index either the passed in interVal is bad or ther is 0 SF.
            return 0.0


if __name__ == "__main__":
    """
    Make sure 3rd parameter is the right list.  Also distance calculation doesn't give the factor.
    """
    
    #fakes = pd.read_csv("/home/tristan/BenResearch/M83/code/textFiles/current_densities.txt")
    #densities = pd.read_csv("/home/tristan/BenResearch/M83/code/textFiles/current_master_densities.txt")

    #matchDensities(2.0, fakes, densities)
    pass

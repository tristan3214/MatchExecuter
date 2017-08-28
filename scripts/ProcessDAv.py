#!/usr/bin/env python
from __future__ import print_function, division, absolute_import

import glob
import subprocess
import sys

import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg") # IMPORTANT for server to be able plot
import matplotlib.pyplot as plt
plt.ioff() # turn interactive maptlotlib off
from scipy.interpolate import interp1d
from astropy.io import fits
import seaborn

#########################
#### Internal imports####
#########################
from PlotSFR import SFH
from MatchParam import MatchParam
from UserParameters import *

__author__ = "Tristan J. Hillis"

"""
This funtion will take in a list that is sent to MatchRunner.py and find the best fit dAv and output it as a THE fit.
It will also plot the change in fit with dAv and Av as well as make cumulative star formation plots for all the plots.
"""

class ProcessDAv(object):

    def __init__(self, path, baseName, photFile, paramFile, bins=22):
        bins = int(bins)
        self.processDAv_general(path, baseName, photFile, paramFile, bins=bins)
        
    def processDAv_general(self, path, baseName, photFile, paramFile, bins):
        """
        Takes in a path with a baseName that will follow standard dAv naming conventions.
        """
        print("BINS:", bins)
        dAvfile = open(path+"best_dAvs.ls", 'a')
        massFile = open(path+"best_mass.ls", 'a')
        metallicity = "z_0-19" # Defines the metallicity to use for plotting isochrones

        path = path.strip("")
        print("PATH:", path)
        files = glob.glob(path+baseName+"_dAv_?-??")

        files = np.asarray([file for file in files if "." not in file]) # get rid of extraneous files ending with a suffix
        #print(files)

        print("FILES:", files)
        
        # order files in increasing dAv
        dAvs = np.asarray([float(file.split("/")[-1].split("_")[-1].replace("-", ".")) for file in files])
        #print(dAvs)

        # sort by increasing dAv
        idxs = np.argsort(dAvs)
        files = files[idxs]
        dAvs = dAvs[idxs]
        #print(files, dAvs)

        # get best fits values
        vec_getBestFit = np.vectorize(self.getBestFit) # vectorize function
        bestFits, bestAvs = vec_getBestFit(files)
        #print(bestFits)

        # make the fit with the best fit value the fit with the main string name.
        best_idx = np.argmin(bestFits)
        best_file = files[best_idx]
        best_files = glob.glob(best_file+"*")

        # print out the SNR with best dAv
        #print(repr(path),path.split("/"))
        best_dAv = dAvs[best_idx]
        best_Av = bestAvs[best_idx]
        dAvfile.write("%s %f %f\n" % (baseName, best_dAv, best_Av))

        # change the names
        new_names = []
        for file in best_files:
            name = file.split("/")[-1].split("_")
            if "." in name[-1]:
                name[-1] = "." + name[-1].split(".")[-1]
                name.pop(-2)
                name = "_".join(name[:-1]) + name[-1]
            else:
                name.pop(-1)
                name.pop(-1)
                name = "_".join(name)
            new_names.append(path+name)

        for j, file in enumerate(best_files):
            name = new_names[j]
            subprocess.call(['cp', file, name])

        plt.rc('font', family='sans-serif')
        params = {'mathtext.default': 'regular' }
        plt.rcParams.update(params)

        csfs = [SFH(file+".zc", bins=bins) for file in files]

        fig = plt.figure(figsize=(18.0, 6.5))
        #fig = plt.figure()
        gs = mpl.gridspec.GridSpec(1, 3, width_ratios=[1.5,1.0,1.0])
        #fig = plt.figure()

        # plot Cumulative stellar mass functions
        rainbow = iter(plt.cm.rainbow(np.linspace(0, 1, len(csfs))))
        #ax = fig.add_subplot(131)
        ax = fig.add_subplot(gs[0])
        for i, csf in enumerate(csfs):
            csf.calculateCSF()
            c = next(rainbow)
            ax.plot(csf.getX(), csf.getY(), color=c, linewidth=1.5, zorder=i/100 + 1)

        ax.set_axis_bgcolor('0.8')
        sm = plt.cm.ScalarMappable(cmap=plt.cm.rainbow, norm=plt.Normalize(vmin=dAvs[0], vmax=dAvs[-1]))
        sm.set_array(dAvs)
        cbar = fig.colorbar(sm)
        cbar.ax.tick_params(labelsize=14)

        plt.ylabel(r"Cumulative Stellar Mass", fontsize=20)
        plt.xlabel("Time (Myrs)", fontsize=20)
        ax.tick_params(labelsize=16)

        # get id for title
        split_path = path.split("/")
        split_path = [item for item in split_path if item != '']
        snr_id = split_path[-1]
        print("ID:", snr_id, split_path)
        #plt.suptitle(snr_id + ": " + baseName)

        #### Plot specific parts for the best dAv
        csf = csfs[best_idx]

        ### Add to the top of the first panel the mass derived from the age using
        # get log years
        log_year = np.arange(6.6, 7.8, 0.05)
        log_year_string = [str(year).replace(".", "-") for year in log_year]

        # get the highest initial mass for each age assuming solar of 0.019
        masses = []
        isochrones = {}
        for year in log_year_string: 
            iso = pd.read_csv("%s/isochrones/"%MATCH_SERVER_DIR + metallicity + "_%s"%year, delim_whitespace=True)
            isochrones[year] = iso
            masses.append(iso['M_ini'].values[-1]) # add the highest mass
        linear_year = 10**log_year / 10**6

        masses = np.asarray(masses)
        plotMasses = np.interp(ax.get_xticks(), linear_year, masses)
        plotMasses = [round(mass,1) for mass in plotMasses]

        #plt.tight_layout()

        # prepare ticks for top x axis
        print("FIRST TICKS:", ax.get_xticks().size, ax.get_xticks())
        ax2_ticks = np.linspace(ax.get_xticks()[0], ax.get_xticks()[-1], 2*ax.get_xticks().size - 1)
        f = interp1d(linear_year, masses, fill_value='extrapolate')
        ax2_mass = np.round(f(ax2_ticks), 2)
        print("TICKS:", ax2_ticks, ax2_mass)
        #ax2_mass = np.round(np.interp(ax2_ticks, linear_year, masses), 2)
        ax2 = ax.twiny()
        ax2.set_xticks(ax2_ticks[::2], minor=False)
        ax2.set_xticklabels(ax2_mass[::2], size=16)
        ax2.xaxis.grid(True, which='major')
        # add minor ticks
        ax2.set_xticks(ax2_ticks[1::2], minor=True)
        ax2.set_xticklabels(ax2_mass[1::2], size=13, minor=True)
        ax2.xaxis.grid(False)

        # hand draw minor grid axis
        minor_top_ticks = ax2.get_xticks(minor=True)
        for i, xtick in enumerate(minor_top_ticks):
            ax.axvline(xtick, linestyle='-.', color='w', zorder=(i+0.1)/100, linewidth=1.2)
        # adjust padding
        ax2.tick_params(which='major', pad=15)
        ax2.tick_params(which='minor', pad=0)
        ax2.set_xlabel(r"Mass ($M_\odot$)", fontsize=20)
        ax2.set_axisbelow(True)

        #plt.ylim([0.0, 1.0])
        #plt.xlim([0, max(ax2_ticks)])
        ax.set_ylim([0.0, 1.0])
        ax.set_xlim([0.0, max(ax2_ticks)])

        #fig.set_width(10)

        # Interpolate the percentiles
        central_mass = None
        if np.all(np.isnan(csf.getY())):
            central_mass = (0, 0, 0)
        else:
            percentiles = self.interpolate([0.84, 0.5, 0.16], csf.getX(), csf.getY())

            ### plot percentiles with center as dotted line and grey band as area of error
            # plot vertical line for 50th percentile
            ax.axvline(x=percentiles[1], linestyle="--", color='0.0')

            # plot vertical translucent red region spanning the error
            ax.axvspan(xmin=percentiles[0], xmax=percentiles[2], color='r', alpha=0.2)

            # get the actual values of mass and display on the graph
            # get the closest log year to the percentiles
            center_between_idx = self.getClosestLogYearIndices(percentiles[1], log_year)
            plus_between_idx = self.getClosestLogYearIndices(percentiles[0], log_year)
            minus_between_idx = self.getClosestLogYearIndices(percentiles[2], log_year)

            center_mass = self.interpMass(percentiles[1], center_between_idx[0], center_between_idx[1], isochrones, log_year_string)
            plus_mass = self.interpMass(percentiles[0], plus_between_idx[0], plus_between_idx[1], isochrones, log_year_string)
            minus_mass = self.interpMass(percentiles[2], minus_between_idx[0], minus_between_idx[1], isochrones, log_year_string)

            central_mass = (plus_mass, center_mass, minus_mass)


            #closest = getClosestLogYearIndex(percentiles, log_year)
            #central_mass = (isochrones[log_year_string[closest[0]]]['M_ini'].values[-1], isochrones[log_year_string[closest[1]]]['M_ini'].values[-1],
            #               isochrones[log_year_string[closest[2]]]['M_ini'].values[-1])

        ax.text(35, 0.9, snr_id, fontsize=20, zorder=10)
        ax.text(30, 0.85, r"$M=%.1f^{+%.1f}_{-%.1f}$" % (central_mass[1], central_mass[0]-central_mass[1], central_mass[1]-central_mass[2]),
                fontsize=20, zorder=10)
        massFile.write("%s %.2f %.2f %.2f\n" % (baseName, central_mass[1], central_mass[0]-central_mass[1], central_mass[1]-central_mass[2]) )

        # plot best fit values vs dAvs
        #ax = fig.add_subplot(132)
        ax = fig.add_subplot(gs[1])
        ax.scatter(dAvs, bestFits, color='k')
        ax.set_axis_bgcolor('0.8')
        plt.ylabel("Fit value (arbitrary)", fontsize=20)
        plt.xlabel("dAv", fontsize=20)
        plt.gca().tick_params(labelsize=16, which='major')

        # plot cmd with photometry file
        #ax = fig.add_subplot(133)
        ax = fig.add_subplot(gs[2])

        #### Get data of field and photometry file #####
        # field should be from background which we get from reading the parameter file
        param = MatchParam(path+paramFile, None, None)
        noback = True

        background_data = None
        if param.parameters['background'] is not None:
            noback = False
            background_path = path + param.parameters['background']
            background_data = np.loadtxt(background_path, unpack=True)

        # get photometry data
        photemetry_data = np.loadtxt(path+photFile, unpack=True)

        # get the number of columns: 2 - one CMD | 3 - 2 CMDs
        numCols = len(photemetry_data)

        # Blue mag will be the lower filter and red_mag will be the higher filter
        blue_phot_mag = None
        blue_field_mag = None
        red_phot_mag = None
        red_field_mag = None

        limit_colors, limit_mag = None, None
        filters = param.filterSet

        if numCols == 2:
            # Assign field/backgroun data
            if not noback:
                blue_field_mag, red_field_mag = background_data[0], background_data[1]
            # Assign photometry data
            blue_phot_mag, red_phot_mag = photemetry_data[0], photemetry_data[1]
            limit_colors, limit_mag = self.magLimitsGreaterFilter(param.parameters[filters[0]+"max"], param.parameters[filters[1]+"max"])
        else: # 2 CMDs which we take the 2nd column as blue and the 3rd column as red
            if not noback:
                blue_field_mag, red_field_mag = background_data[1], background_data[2]
            blue_phot_mag, red_phot_mag = photemetry_data[1], photemetry_data[2]
            limit_colors, limit_mag = self.magLimitsGreaterFilter(param.parameters[filters[1]+"max"], param.parameters[filters[2]+"max"])

        # Create masks for the field and photemetry data to filter out values of 99.99 or to large of magnitudes
        if not noback:
            field_mask = (blue_field_mag < 30.0) & (red_field_mag < 30.0)
        phot_mask = (blue_phot_mag < 30.0) & (red_phot_mag < 30.0)

        # Apply mask
        if not noback:
            blue_field_mag, red_field_mag = blue_field_mag[field_mask], red_field_mag[field_mask]
        blue_phot_mag, red_phot_mag = blue_phot_mag[phot_mask], red_phot_mag[phot_mask]

        # Plot field data as 2d histogram
        if not noback:
            H, xedges, yedges = np.histogram2d(blue_field_mag-red_field_mag, red_field_mag, bins=[75, 75])
            color = plt.cm.gray
            color.set_bad("w")
            col = ax.pcolormesh(xedges, yedges, np.ma.masked_values(H.T, 0), cmap=color)
            cbar = plt.colorbar(col)

            plt.xlim([xedges.min(), xedges.max()])
            plt.ylim([yedges.min(), yedges.max()])

        else:
            plt.xlim([(blue_phot_mag-red_phot_mag).min(), (blue_phot_mag-red_phot_mag).max()])
            plt.ylim([red_phot_mag.min(), red_phot_mag.max()])

        ax.scatter(blue_phot_mag-red_phot_mag, red_phot_mag, color='r', s=12)
        
        ax.plot(limit_colors, limit_mag, linestyle='--', color='green')

        if numCols == 2:
            plt.xlabel("%s - %s" % (filters[0], filters[1]), fontsize=18)
            plt.ylabel(filters[1], fontsize=18)
        else:
            plt.xlabel("%s - %s" % (filters[1], filters[2]), fontsize=18)
            plt.ylabel(filters[2], fontsize=18)
            
        ax.invert_yaxis()
        plt.gca().tick_params(labelsize=16, which='major')    
        plt.tight_layout()

                
        plt.savefig(path+baseName+"_bestDAv")

        dAvfile.close()
        massFile.close()
    
    def magLimitsGreaterFilter(self, low, high):
        # define points
        x1 = 0
        y1 = low
        x2 = low - high
        y2 = high

        slope = (y2 - y1) / (x2 - x1)
        intercept = y1

        x = np.linspace(-10.0, x2, 100)
        y = np.linspace(y2, y2, 100)

        lin = lambda x_val, m, b: m*x_val + b
        x_alt = np.linspace(x2, 10, 100)
        y_alt = lin(x_alt, slope, intercept)

        x = np.append(x, x_alt)
        y = np.append(y, y_alt)

        return x, y

    def interpolate(self, interpVals, x, y):
        """
        Returns the interpereted x value about the passed in interpVal(s).
        """
        linear = lambda y: (y-b) / m
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

    def getClosestLogYearIndices(self, age, log_year):
        """
        Pass in a year with an array of the available log years, "log_year" that will be compared.
        Percentiles are assumed to be in millions of years and will be converted to log_year.
        This returns a tuple of indices of where the passed in age falls between in the given available log years.
        """
        #print("AGES:", age)
        age = np.log10(np.asarray(age) * 10**6) # convert to log years

        distances = np.abs(log_year - age)

        first_closest_idx = np.argmin(distances)

        # set the first min to infinity to then find the next smallest number
        distances[first_closest_idx] = np.infty

        second_closest_idx = np.argmin(distances)

        return (first_closest_idx, second_closest_idx)

    def interpMass(self, age_to_interp, age1_idx, age2_idx, isochrones, log_year_string):
        # turn age to interp into log years
        age_to_interp = np.log10(age_to_interp * 10**6) # convert to log years
        log_years = [float(str.replace("-",".")) for str in log_year_string]

        ages = [float(log_years[age1_idx]), float(log_years[age2_idx])]
        masses = [isochrones[log_year_string[age1_idx]]['M_ini'].values[-1], isochrones[log_year_string[age2_idx]]['M_ini'].values[-1]]

        f = interp1d(ages, masses)
        mass_interp = f(age_to_interp)

        return mass_interp


    def getClosestLogYearIndex(self, percentiles, log_year):
        """
        Pass in percentiles as (84th, 50th, 16th) with a log_year that will be compared to.
        Percentiles are assumed to be in millions of years and will be converted to log_year.
        """
        percentiles = np.log10(np.asarray(percentiles) * 10**6) # convert to log years
        #print("CONVERTED PERCENTILES:", percentiles)

        distances = (np.abs(log_year - percentiles[0]), np.abs(log_year - percentiles[1]), np.abs(log_year - percentiles[2]))
        #print("DISTANCES:", distances)

        idx = (np.argmin(distances[0]), np.argmin(distances[1]), np.argmin(distances[2]))
        return idx

    def getBestFit(self, fileName):
        f = open(fileName+".co", 'r')
        for line in f:
            if "Best" in line: # reached line where there is the best fit number
                # get fit value 
                fit = line.split()[-1]
                val = fit.split("=")[-1]

                # get Av value
                Av = line.split()[-3]
                Av = Av.split("=")[-1][:-1]

                return (float(val), float(Av))
            
def main():
    path = sys.argv[1]
    baseName = sys.argv[2]
    photometry = sys.argv[3]
    param_file = sys.argv[4]
    bins = sys.argv[5]

    ProcessDAv(path, baseName, photometry, param_file, bins=bins)

if __name__ == "__main__":
    main()


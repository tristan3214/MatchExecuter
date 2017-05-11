#!/astro/apps6/anaconda/bin/python2
from __future__ import print_function, division, absolute_import

import glob
import os
import sys

import numpy as np
import pandas as pd

"""
Synopsis
--------
Works on Python 2.7 and Python 3.x.

This is a module that helps to quickly script the making of new parameter files.  Suppose you have a lot of MATCH fits and each one is slightly
different.  If you feed MatchParam a master parameter file that reflects the common across the fits you can tweak the fit specific
parameters.  SSP parameter files can be fed as long as you specify to the MatchParam that it is an SSP parameter file. 

It includes advanced usages to make calculating the brightest and dimmest magnitudes per filter when you pass a photometry and/or
fake star file (See UsingMatchParam.py in "example")


Usage (For more advanced usage like changing exclude gates see UsingMatchParam.py in the "example" directory.)
-----
# This shows how to feed a fully filled out MATCH parameter file, change something basic, and then save it.
>>> from MatchParam import MatchParam

>>> param = MatchParam("/path/to/your/param.param")
>>> param.change("dAv", 0.1)
>>> param.save(name="new_param.param") # saves in CWD
>>> param.save(path="/to/save/directory", name="new_param.param") # Saves in desired directory

# To retrieve a basic key's value like the minimum distance modulus value.
>>> param = MatchParam("/path/to/your/param.param")
>>> minDistMod = param.parameters['m-Mmin']
>>> minDistMod # an example
26.0
>>> type(minDistMod)
<type 'float'>
# OR
>>> minDistMod = param.get('m-Mmin')
>>> type(minDistMod) # check the type
<type 'float'>

Keys (Use the printKeys function in MatchParam to see the object's instance of keys)
----
m-Mmin m-Mmax d(m-M) Avmin Avmax dAv
logZmin logZmax dlogZ [initMin initMax presMin presMax]
BF Bad0 Bad1
Ncmds
Vstep V-Istep fake_sm V-Imin V-Imax V,I  (per CMD)
Vmin Vmax V                              (per filter)
Imin Imax I                              (per filter)
Nexclude exclude Ncombine combine (per CMD)
Ntbins
Tstart Tf (for each time bin)
lLine1 lLine2 scalebackground (optional background bins (takes 3 different numbers with optional background see MATCH README))

Caviates:
Vstep V-Istep fake_sm V-Imin V-Imax
Vmin Vmax V
Imin Imax I

The above vary with the number of CMDs used.
when Ncmds = 1 Vstep, V-Istep, fake_sm, V-Imin V-Imax are as is
when Ncmds > 1 Vstep, V-Istep, fake_sm, V-Imin, V-Imax have the CMD num appended (eg Vstep_1, Vstep_2, etc.)

Vmin Vmax V
Imin Imax I
The min and max keys always have the filter name prefixed (eg UVIS438Wmin and UVIS438max)
"""

class MatchParam(object):
    """This class reads from a "master" MATCH parameter file.  Supports ssp style parameter files.

    Basic Usage
    -----------
    >>> param = MatchParam("/path/to/your/param.param")
    >>> param.change("dAv", 0.1)
    >>> param.save(name="new_param.param") # saves in CWD
    """
    def __init__(self, default, photFile=None, fakeFile=None, useBackgroundMin=False, ssp=False):
        """Pass in a "master" parameter file to script smaller changes and save to new parameter files.

        Parameters
        ----------
        default : string
                  Path to th "master" parameter file to be parsed.
        photFile : {string} (optional) 
                   Specify the MATCH photometry file path associated with the parameter file.
        fakeFile : {string} (optional)
                   Specify the MATCH fake star file path associated with the parameter file.
        useBackgroundMin : {boolean}, (optional) 
                           Set to True if you want the brightest mag to be calculated using a background given
                           in the parameter file.  Else the photometry file is used during this calculation. 
                           See use cases above in the module docstring.
        ssp : {boolean}
              When passing in an ssp parameter file set this to True.
        

        Attributes
        ----------
        default : string
                  References the MATCH file path.
        phot : string
               Reference the MATCH photometry file if given.
        fake : string
               Reference the MATCH fake file if given.
        parameters : dict
                     Holds all the parameters parsed from the passed in parameter file.  Keywords follow the names in the
                     MATCH README.  See module docstring for all the keywords and nuances in calling different filters.
        filterset : list
                    Holds the list of filters parsed as strings.
        zinc : boolean
               Tells the user if their parameter file is setup for zinc (ie 7 entries instead of 3 on the metallicity line)
        ssp : boolean
              Sets the parameter object to be ssp.
        savedTo : string
                  Holds the path full path to the saved parameter file.  Set when save is called.
        name : string
               Holds the name of the parameter file.  Set when save is called.

        """
        # Constructs a MATCH parameter file object from a default parameter file to reference the settings.
        self.default = default # parameter file
        self.phot = photFile # photometry file to be fed to calcsfh
        self.fake = fakeFile # fake file to be fed to calcsfh
        
        # dictionary that will fill with all the parameters (some are to be added in parseDefalut method)
        self.parameters = {"m-Mmin":None, "m-Mmax":None, "d(m-M)":None, "Avmin":None, "Avmax":None, "dAv":None,
                           "logZmin":None, "logZmax":None, "dlogZ":None, "initMin":None, "initMax":None, "presMin":None, "presMax":None,
                           "BF":None, "Bad0":None, "Bad1":None,
                           "Ncmds":None,
                           "Nexclude":None, "exclude":[], "Ncombine":None, "combine":[],
                           "Ntbins":None,
                           "lLine_1":None, "lLine_2":None, "scale":None, "background":None}

        # Holds the filters being used in the parameter file.
        self.filterSet = []
        
        # flags to tell if there is something like zinc
        self.zinc = False # auto-detected by parsing the parameter file
        self.ssp = ssp # if a an ssp flag is passed then this will be set to True by an external program

        self.savedTo = None
        self.name = None
        
        #Internal flags
        self._calculateMaxOrMin = False
        self._useBackgroundMin=useBackgroundMin

        self._parseDefault()

    def change(self, key, value):
        """Change one of the values within the parameter file.

        Parameters
        ----------
        key : string
              This should be a valid key.
        value : type dependent on the keys

        Return
        ------
        None

        Example
        -------
        >>> param = MatchParam("your_parameter.param")
        >>> param.change('dAv', 0.1) # This would change the Av step to 0.1.
        """
        if key in self.parameters.keys():
            if self.parameters[key] is not None:
                valType = type(self.parameters[key])
                self.parameters[key] = valType(value)
            else:
                self.parameters[key] = value
        else:
            raise KeyError("Key not found:", key)
        
        return None

    def get(self, key):
        """Pass in a key to retrieve the value of from the self.parameters dictionary.  Raises exception if it is not
        a valid key.
        
        Parameters
        ----------
        key : string
              Must be a valid parameter key input.
        
        Return
        ------
        {string, float} : type depends on the parameter
                          Returns a the value associated with the passed in key.
        """
        if key in self.parameters.keys():
            return self.parameters[key]
        else:
            raise KeyError("Did not find key in object.parameters")

    def printKeys(self):
        """Print instances keys.  Use this to visually see what keys you can use.  It prints out in the 
        style of the MATCH parameter file.

        Parameters
        ----------
        None

        Return
        ------
        None
        """
        # line one (m-Mmin m-Mmax d(m-M) Avmin Avmax dAv)
        print("m-Mmin m-Mmax d(m-M) Avmin Avmax dAv")

        # line two (logZmin logZmax dlogZ) w/zinc (logZmin logZmax dlogZ initMin initMax presMin presMax)
        if not self.zinc or self.ssp:
            print("logZmin logZmax dlogZ")
        else:
            print("logZmin logZmax dlogZ initMin initMax presMin presMax")
            
        # line three (BF Bad0 Bad1)
        print("BF Bad0 Bad1")

        # line four (Ncmds)
        print("Ncmds")

        # line five to (five + Ncmds) (Vstep V-Istep fake_sm V-Imin V-Imax V,I  (per CMD))
        if self.parameters["Ncmds"] == 1:
            print("Vstep V-Istep fake_sm V-Imin V-Imax V I")
        else:
            for i in range(int(self.parameters["Ncmds"])):
                print("Vstep_" + str(i+1) + " V-Istep_" + str(i+1) + " fake_sm_" + str(i+1) + " V-Imin_" + str(i+1) + \
                      " V-Imax_" + str(i+1) + " V_" + str(i+1) + " I_" + str(i+1))
                
        # lines for each filter (filterMin filterMax filter(per filter))
        for i, filter in enumerate(self.filterSet):
            print(filter + "min " + filter + "max " + filter)

        # exclude/combine gates (Nexclude exclude Ncombine combine (per CMD))
        print("Nexclude exclude Ncombine combine")

        # number of time bins (Ntbins)
        print("Ntbins")

        # time bins
        print("    tstart tend (passed in as lists of start and end times of same size)")
        
        # last line
        if self.parameters['scale'] is not None:
            print("lLine_1 lLine_2 scale[background]")
    

        
    def save(self, path=None, name=None):
        """Used to save the current MatchParam object into a standard MATCH parameter file.

        Parameters
        ----------
        path : {string}
               Path to save directory.
        name : {string}
               Specify a name for the new parameter file.

        Return
        ------
        None
        """
        if path is None:
            path = os.getcwd() + "/"
        if name is None:
            # defualts to parameter file named parameters_XX.param and creates symbolic link
            name = self._iterateParameter()
        if path[-1] != "/":
            path += "/"
            
        self.savedTo = path + name
        self.name = name
        f = open(path + name, 'w')

        # line one (IMF m-Mmin m-Mmax d(m-M) Avmin Avmax dAv)
        f.write("%.2f %.2f %.2f %.3f %.3f %.2f\n" % (self.parameters["m-Mmin"], self.parameters["m-Mmax"], self.parameters["d(m-M)"],
                                                     self.parameters["Avmin"], self.parameters["Avmax"],self.parameters["dAv"]))

        # line two (logZmin logZmax dlogZ) w/zinc (logZmin logZmax dlogZ initMin initMax presMin presMax)
        if not self.zinc or self.ssp:
            f.write("%.2f %.2f %.2f\n" % (self.parameters["logZmin"], self.parameters["logZmax"], self.parameters["dlogZ"]))
        else:
            f.write("%.2f %.2f %.2f %.2f %.2f %.2f %.2f\n" % (self.parameters["logZmin"], self.parameters["logZmax"],
                                                self.parameters["dlogZ"], self.parameters["initMin"],
                                                self.parameters["initMax"], self.parameters["presMin"],
                                                self.parameters["presMax"]))
        # line three (BF Bad0 Bad1)
        f.write("%.2f %f %f\n" % (self.parameters["BF"], self.parameters["Bad0"], self.parameters["Bad1"]))

        # line four (Ncmds)
        f.write("%d\n" % (self.parameters["Ncmds"]))

        # line five to (five + Ncmds) (Vstep V-Istep fake_sm V-Imin V-Imax V,I  (per CMD))
        if self.parameters["Ncmds"] == 1:
            f.write("%.2f %.2f %d %.2f %.2f %s,%s\n" % (self.parameters["Vstep"], self.parameters["V-Istep"],
                                                self.parameters["fake_sm"], self.parameters["V-Imin"],
                                                self.parameters["V-Imax"], self.parameters["V"],
                                                self.parameters["I"]))
        else:
            for i in range(int(self.parameters["Ncmds"])):
                f.write("%.2f %.2f %d %.2f %.2f %s,%s\n" % (self.parameters["Vstep_" + str(i+1)], self.parameters["V-Istep_" + str(i+1)],
                                                    self.parameters["fake_sm_" + str(i+1)], self.parameters["V-Imin_" + str(i+1)],
                                                    self.parameters["V-Imax_" + str(i+1)], self.parameters["V_" + str(i+1)],
                                                    self.parameters["I_" + str(i+1)]))
        # lines for each filter (filterMin filterMax filter(per filter))
        for i, filter in enumerate(self.filterSet):
            f.write("%.1f %.1f %s\n" % (self.parameters[filter + "min"], self.parameters[filter + "max"],
                                    self.parameters[filter]))

        # exclude/combine gates (Nexclude exclude Ncombine combine (per CMD))
        for i in range(int(self.parameters["Ncmds"])):
            f.write("%d" % self.parameters["Nexclude"])
            if self.parameters["Nexclude"] != 0:
                exclude = self.parameters["exclude"]
                for j in range(len(exclude)//2):
                    f.write(" %.2f %.2f" % (exclude[2*j], exclude[2*j + 1]))
                    
            f.write(" %d" % self.parameters["Ncombine"])
            if self.parameters["Ncombine"] != 0:
                combine = self.parameters["combine"]
                for j in range(len(combine)//2):
                    f.write(" %.2f %.2f" % (combine[2*j], combine[2*j + 1]))
            f.write("\n")

        # number of time bins (Ntbins)
        f.write("%d\n" % self.parameters["Ntbins"])

        # time bins
        start = self.parameters["tstart"]
        end = self.parameters["tend"]
        for i, time in enumerate(start):
            f.write("  %.2f  %.2f\n" % (time, end[i]))

        # last line
        f.write("%s %s %s" % (self.parameters["lLine_1"], self.parameters["lLine_2"], str(self.parameters["scale"])))
        if self.parameters["background"] is not None:
            f.write("%s\n" % self.parameters["background"])
        else:
            f.write("\n")

        f.close()

    def print(self):
        """This prints the currently loaded parameters in the format of the MATCH parameter file.
        """
        # line one (m-Mmin m-Mmax d(m-M) Avmin Avmax dAv)
        print("%.2f %.2f %.2f %.3f %.3f %.2f" % (self.parameters["m-Mmin"], self.parameters["m-Mmax"], self.parameters["d(m-M)"],
                                                 self.parameters["Avmin"], self.parameters["Avmax"],self.parameters["dAv"]))

        # line two (logZmin logZmax dlogZ) w/zinc (logZmin logZmax dlogZ initMin initMax presMin presMax)
        if not self.zinc or self.ssp:
            print("%.2f %.2f %.2f" % (self.parameters["logZmin"], self.parameters["logZmax"], self.parameters["dlogZ"]))
        else:
            print("%.2f %.2f %.2f %.2f %.2f %.2f %.2f" % (self.parameters["logZmin"], self.parameters["logZmax"],
                                                          self.parameters["dlogZ"], self.parameters["initMin"],
                                                          self.parameters["initMax"], self.parameters["presMin"],
                                                          self.parameters["presMax"]))
        # line three (BF Bad0 Bad1)
        print("%.2f %f %f" % (self.parameters["BF"], self.parameters["Bad0"], self.parameters["Bad1"]))

        # line four (Ncmds)
        print("%d" % (self.parameters["Ncmds"]))

        # line five to (five + Ncmds) (Vstep V-Istep fake_sm V-Imin V-Imax V,I  (per CMD))
        if self.parameters["Ncmds"] == 1:
            print("%.2f %.2f %d %.2f %.2f %s,%s" % (self.parameters["Vstep"], self.parameters["V-Istep"],
                                                    self.parameters["fake_sm"], self.parameters["V-Imin"],
                                                    self.parameters["V-Imax"], self.parameters["V"],
                                                    self.parameters["I"]))
        else:
            for i in range(int(self.parameters["Ncmds"])):
                print("%.2f %.2f %d %.2f %.2f %s,%s" % (self.parameters["Vstep_" + str(i+1)], self.parameters["V-Istep_" + str(i+1)],
                                                        self.parameters["fake_sm_" + str(i+1)], self.parameters["V-Imin_" + str(i+1)],
                                                        self.parameters["V-Imax_" + str(i+1)], self.parameters["V_" + str(i+1)],
                                                        self.parameters["I_" + str(i+1)]))
        # lines for each filter (filterMin filterMax filter(per filter))
        for i, filter in enumerate(self.filterSet):
            print("%.1f %.1f %s" % (self.parameters[filter + "min"], self.parameters[filter + "max"],
                                    self.parameters[filter]))

        # exclude/combine gates (Nexclude exclude Ncombine combine (per CMD))
        s = ""
        for i in range(int(self.parameters["Ncmds"])):
            s += "%d" % self.parameters["Nexclude"]
            if self.parameters["Nexclude"] != 0:
                exclude = self.parameters["exclude"]
                for j in range(len(exclude)//2):
                    s += " %.2f %.2f" % (exclude[2*j], exclude[2*j + 1])
                    
            s += " %d" % self.parameters["Ncombine"]
            if self.parameters["Ncombine"] != 0:
                combine = self.parameters["combine"]
                for j in range(len(combine)//2):
                    s += " %.2f %.2f" % (combine[2*j], combine[2*j + 1])
            if i + 1 != self.parameters["Ncmds"]:
                s += "\n"
        print(s)

        # number of time bins (Ntbins)
        print("%d" % self.parameters["Ntbins"])

        # time bins
        start = self.parameters["tstart"]
        end = self.parameters["tend"]
        for i, time in enumerate(start):
            print("  %.2f  %.2f" % (time, end[i]))

        # last line
        if self.parameters['scale'] is not None:
            if self.parameters['background'] is not None:
                print("%s %s %s%s" % (self.parameters["lLine_1"], self.parameters["lLine_2"], str(self.parameters["scale"]),
                                      str(self.parameters['background'])))
            else:
                print("%s %s %s" % (self.parameters["lLine_1"], self.parameters["lLine_2"], str(self.parameters["scale"])))


    def _parseDefault(self):
        """
        Go through defualt parameter file and populate dictionary of parameters.
        """
        f = open(self.default, 'r')
        params = None
        
        # line one (IMF m-Mmin m-Mmax d(m-M) Avmin Avmax dAv)
        line = self._checkForEnd(f.readline())
        try:
            params = list(map(float, line.split()))
            if len(params) < 6 or len(params) > 6:
                print("Missing/extra paramter(s) in line one of default parameter file:")
                print(line)
                sys.exit(1)
            else:

                self.parameters["m-Mmin"] = params[0]
                self.parameters["m-Mmax"] = params[1]
                self.parameters["d(m-M)"] = params[2]
                self.parameters["Avmin"] = params[3]
                self.parameters["Avmax"] = params[4]
                #print("param 6", params[5])
                self.parameters["dAv"] = params[5]

        except ValueError:
            print("Could not convert one of the arguments to a float:")
            print(line)
            sys.exit(1)

        # line two (logZmin logZmax dlogZ) w/zinc (logZmin logZmax dlogZ initMin initMax presMin presMax)
        line = self._checkForEnd(f.readline())
        try:
            params = list(map(float, line.split()))
            size = len(params)
            if size > 3: # zinc flag should be specified
                self.zinc = True
                if size > 7:
                    print("Extra parameter(s) in line two of default parameter file:")
                    print(line)
                    sys.exit(1)
                else: # add metallicity args plus zinc args
                    self.parameters["logZmin"] = params[0]
                    self.parameters["logZmax"] = params[1]
                    self.parameters["dlogZ"] = params[2]
                    self.parameters["initMin"] = params[3]
                    self.parameters["initMax"] = params[4]
                    self.parameters["presMin"] = params[5]
                    self.parameters["presMax"] = params[6]
            else:
                if size < 3:
                    print("Missing parameter(s) in line two of default parameter file:")
                    print(line)
                    sys.exit(1)
                else: # add metallicity args w/o zinc args
                    self.parameters["logZmin"] = params[0]
                    self.parameters["logZmax"] = params[1]
                    self.parameters["dlogZ"] = params[2]
        except ValueError:
            print("Could not convert a float in line one of the defualt parameter file:")
            print(line)
            sys.exit(1)

        # line 3 (BF Bad0 Bad1)
        line = self._checkForEnd(f.readline())
        try:
            params = list(map(float, line.split()))
            size = len(params)
            if size > 3 or size < 3:
                print("Missing/extra paramter(s) in line three of default parameter file:")
                print(line)
                sys.exit(1)
            else:
                self.parameters["BF"] =  params[0]
                self.parameters["Bad0"] = params[1]
                self.parameters["Bad1"] = params[2]
        except ValueError:
            print("Could not convert a float in line one of the defualt parameter file:")
            print(line)
            sys.exit(1)

        # line 4 (Ncmds)
        line = self._checkForEnd(f.readline())
        try:
            params = list(map(float, line.split()))
            size = len(params)
            if size > 1 or size < 1:
                print("Missing/extra paramter(s) in line three of default parameter file:")
                print(line)
                sys.exit(1)
            else:
                self.parameters["Ncmds"] = params[0]
        except ValueError:
            print("Could not convert an int in line four of the default paramter file:")
            print(line)
            sys.exit(1)

        # line 5 to Ncmds (Vstep V-Istep fake_sm V-Imin V-Imax V,I  (per CMD))
        numCMDs = int(self.parameters["Ncmds"])
        for i in range(numCMDs):
            line = self._checkForEnd(f.readline())
            try:
                params = list(map(str, line.split()))
                size = len(params)
                if size > 6 or size < 6:
                    print("Missing/extra paramter(s) in line three of default parameter file:")
                    print(line)
                    sys.exit(1)
                else:
                    for j in range(size):
                        if j != 5:
                            params[j] = float(params[j])
                        else:
                            params[j] = str(params[j])
                    if numCMDs == 1: # keep normal naming scheme
                        self.parameters["Vstep"] = params[0]
                        self.parameters["V-Istep"] = params[1]
                        self.parameters["fake_sm"] = params[2]
                        self.parameters["V-Imin"] = params[3]
                        self.parameters["V-Imax"] = params[4]
                        filters = params[5].split(",")
                        self.parameters["V"] = filters[0]
                        self.parameters["I"] = filters[1]
                    else: # add numbers at the end e.g. V_1, V_2
                        self.parameters["Vstep_%d" % (i + 1)] = params[0]
                        self.parameters["V-Istep_%d" % (i + 1)] = params[1]
                        self.parameters["fake_sm_%d" % (i + 1)] = params[2]
                        self.parameters["V-Imin_%d" % (i + 1)] = params[3]
                        self.parameters["V-Imax_%d" % (i + 1)] = params[4]
                        filters = params[5].split(",")
                        self.parameters["V_%d" % (i + 1)] = filters[0]
                        self.parameters["I_%d" % (i + 1)] = filters[1]                
            except ValueError:
                print("Conversion of one of the arguments went wrong:")
                print(line)
                sys.exit(1)

        # line Ncmds to number of unique filters (Vmin Vmax V (per filter) # happens for every unique filter)
        filterSet = []
        seen = set()
        for i in range(numCMDs):
            if numCMDs == 1:
                filterV = self.parameters["V"]
                filterI = self.parameters["I"]
                if filterV not in seen:
                    filterSet.append(filterV)
                    seen.add(filterV)
                if filterI not in seen:
                    filterSet.append(filterI)
                    seen.add(filterI)
            else:
                filterV = self.parameters["V_%d" % (i + 1)]
                filterI = self.parameters["I_%d" % (i + 1)]
                if filterV not in seen:
                    filterSet.append(filterV)
                    seen.add(filterV)
                if filterI not in seen:
                    filterSet.append(filterI)
                    seen.add(filterI)

        self.filterSet = filterSet
        for i, filter in enumerate(filterSet):
            line = self._checkForEnd(f.readline())
            params = list(map(str, line.split()))
            size = len(params)
            if size > 3 or size < 3:
                print("Missing/extra paramter(s) in line %d of default parameter file:" % (4 + numCMDs + i))
                print(line)
                sys.exit(1)

            minsAndMax = params[:2]
            if not self._isStringFloat(minsAndMax[0]):
                self.parameters[filter + "min"] = "filterMin" # This is calculated after we are done parsing.
                self._calculateMaxOrMin = True
            else:
                self.parameters[filter + "min"] = float(minsAndMax[0])

            if not self._isStringFloat(minsAndMax[1]):
                if self.fake is not None:
                    completeness = self._calculateComp(numCMDs, 50) # feed the number of CMDs and the completness limit.
                    self.parameters[filter + "max"] = completeness[i]
                    self._calculateMaxOrMin = True
                else:
                    raise GetMagError("Tried to calculate completeness but there is no passed in fake star file.")
            else:
                self.parameters[filter + "max"] = float(minsAndMax[1])

            self.parameters[filter] = filter

        # exclude/combine gates (Nexclude exclude Ncombine combine (per CMD))
        excludePoints = []
        combinePoints = []
        for i in range(numCMDs):
            line = self._checkForEnd(f.readline())
            try:
                count = 0
                params = list(map(float, line.split()))

                self.parameters["Nexclude"] = int(params[0])
                count += 1

                if self.parameters["Nexclude"] != 0:
                    for j in range(4*self.parameters["Nexclude"]):
                        excludePoints.append(params[count])
                        excludePoints.append(params[count+1])
                        count += 2
                    self.parameters["exclude"] = excludePoints
                    #print(self.parameters["exclude"])
                    
                if not params[count].is_integer():
                    print("Ncombine found to not be an integer this suggests user input error...")
                    print(line)
                    sys.exit(1)

                self.parameters["Ncombine"] = int(params[count])
                count += 1

                if self.parameters["Ncombine"] != 0:
                    for j in range(4*self.parameters["Ncombine"]):
                        combinePoints.append(params[count])
                        combinePoints.append(params[count+1])
                        count += 2
                    #self.parameters["combine"] = combinePoints
            except ValueError:
                print("Could not convert float(s) in exclude/combine gates line of the defualt parameter file:")
                print(line)
                sys.exit(1)

        # number of time bins (Ntbins)
        line = self._checkForEnd(f.readline())
        try:
            params = list(map(int, line.split()))
            size = len(params)
            if size > 1 or size < 1:
                print("Missing/extra paramter(s) in line %d of default parameter file:" % (4 + numCMDs + i))
                print(line)
                sys.exit(1)
            self.parameters["Ntbins"] = params[0]

        except ValueError:
            print("Could not convert int in time bin count line of the defualt parameter file:")
            print(line)
            sys.exit(1)

        # time bins
        start = [] # beginning of time bin
        end = [] # end of time bin
        for i in range(self.parameters["Ntbins"]):
            line = self._checkForEnd(f.readline())
            try:
                params = list(map(float, line.split()))
                size = len(params)
                if size > 2 or size < 2:
                    print("Missing/extra paramter(s) in line %d of default parameter file:" % (4 + numCMDs + i))
                    print(line)
                    sys.exit(1)

                start.append(params[0])
                end.append(params[1])
            except ValueError:
                print("Could not convert a float for time bins:")
                print(line)
                sys.exit(1)
        self.parameters["tstart"] = start
        self.parameters["tend"] = end

        # last line
        try:
            line = self._checkForEnd(f.readline())
            try: # no background given
                params = list(map(str, line.split()))
                size = len(params)
                if size > 3 or size < 3:
                    print("Missing/extra paramter(s) in last line")
                    print(line)
                    sys.exit(1)
                self.parameters["lLine_1"] = params[0]
                self.parameters["lLine_2"] = params[1]
                idx = self._testTillString(params[2])

                if idx is not None: # if the returned idx is None then no string was found in the last line arg3
                    try:
                        self.parameters["scale"] = float(params[2][:idx])
                        self.parameters["background"] = params[2][idx:]                        
                    except ValueError: # this assumes somebody indicates "scale" in last line to determine the scale at a later time
                        self.parameters["scale"] = None
                        self.parameters["background"] = params[2][5:] # "scale" is 5 char long
                else:
                    self.parameters["scale"] = float(params[2])

            except ValueError: # potential background
                print("Could not convert to string in last line:")
                print(line)
                sys.exit(1)
        except EOFError:
            #print("No background line given")
            pass

        f.close()

        # Calculate the magnitude mins (brightest magnitude) if we find a string still there
        # recalculated the max magnitudes for the parameter file in the existence of a background
        calculateMax = []
        for filter in self.filterSet:
            try:
                float(self.parameters[filter + "min"])
                calculateMax.append(False)
            except ValueError:
                calculateMax.append(True)
        if True in calculateMax:
            if self.phot is not None:
                maxes = self._calculateMaxes(numCMDs)
                for i, filter in enumerate(self.filterSet):
                    if calculateMax[i] == True:
                        self.parameters[filter + "min"] = maxes[i]
            else:
                raise GetMagError("Tried to calculate the min mag but there was no passed in photometry file.")
                        
        
    def _testTillString(self, s):
        """
        Takes in a string s and will check when a string starts assuming there is a float before it.
        """
        size = len(s)
        idx = None
        for i in range(size):
            substring = s[:i+1]
            if i == 0 and substring == "-": # if there is a negative in front
                continue
            try:
                float(substring)
            except ValueError:
                idx = i
                break
        return idx
                
    def _checkForEnd(self, s):
        #print(s.strip())
        if s == "":
            #print("Reached end of file unexpectedly in default parameter file...exiting")
            raise EOFError("End of parameter file")
        elif s == "\n":
            print("Unexpected blank line in default parameter file...exiting")
            sys.exit(1)
        else:
            #print(s.strip())
            return s.strip()

    def _calculateMaxes(self, n):
        """
        Calculates the brightest magnitude in the phot file, which is essentially the minium.  Passed in is the number of cmds.
        2 CMDs gives 3 filters and 1 CMD gives. If there is a detected background file then we use it to compute the brightest.
        """
        file_to_use = self.phot
        if self.parameters['background'] is not None and self._useBackgroundMin:
            file_to_use = self.parameters['background']
                
        if n == 1:
            lowest_cmd, higher_cmd = np.loadtxt(file_to_use, usecols=[0,1], unpack=True)

            lowest_min = lowest_cmd.min()
            higher_min = higher_cmd.min()

            return [lowest_min, higher_min]
        
        else:# when the number of cmds is 2 we grab 3 filters
            lowest_cmd, middle_cmd, largest_cmd = np.loadtxt(file_to_use, usecols=[0, 1, 2], unpack=True)

            lowest_min = lowest_cmd.min()
            middle_min = middle_cmd.min()
            largest_min = largest_cmd.min()

            return [lowest_min, middle_min, largest_min]

    def _calculateComp(self, n, completeness):
        """
        Calculates the 50 percent completeness limit for the passed in fake file. The passed in value is the number of CMDs.
        If the number is 1 the the fake file has 4 columns and it is 6 if n is 3.
        """
        # change this to get finer/coarser binning
        size_of_bin = 0.1 # set size of bin

        # read in fake file columns
        if n == 1:
            V_in, I_in, V_outin, I_outin = np.loadtxt(self.fake, usecols=[0,1,2,3], unpack=True)

            V_comp = self._getCompleteness(V_in, V_outin, size_of_bin, completeness)

            I_comp = self._getCompleteness(I_in, I_outin, size_of_bin, completeness)

            return [V_comp, I_comp]

            
        else:
            f336_in, f438_in, f814_in, f336_outin, f438_outin, f814_outin = np.loadtxt(self.fake,
                                                                                       usecols=[0, 1, 2, 3, 4, 5], unpack=True)

            ### Get the 50% completeness of F336W
            f336_50 = self._getCompleteness(f336_in, f336_outin, size_of_bin, completeness)

            #### Get the 50% completeness for F438W
            f438_50 = self._getCompleteness(f438_in, f438_outin, size_of_bin, completeness)

            ### Get the 50% completeness for F814W
            f814_50 = self._getCompleteness(f814_in, f814_outin, size_of_bin,completeness)

            return [f336_50, f438_50, f814_50]


    def _getCompleteness(self, mag_in, mag_outin, size_of_bin, completeness):
        good_idx = np.where(mag_in < 30.0)[0]
        mag_in, mag_outin = mag_in[good_idx], mag_outin[good_idx]
        mag_brightest, mag_faintest = mag_in.min(), mag_in.max()
        number_of_bins = int(np.ceil((mag_faintest - mag_brightest) / size_of_bin))

        mag_mag = []
        mag_fraction = []

        begin_mag = mag_brightest
        end_mag = mag_brightest + size_of_bin
        for i in range(number_of_bins):
            idx = np.where((mag_in >= begin_mag) & (mag_in < end_mag))[0]
            recovered = mag_outin[idx]
            recovered = recovered[(recovered>=-1.0) & (recovered<=1.0)]
            if i == 0:
                mag_mag.append(begin_mag)
                mag_mag.append(end_mag)

                if idx.size <= 0:
                    mag_fraction.append(np.nan)
                    mag_fraction.append(np.nan)
                else:
                    mag_fraction.append(recovered.size / idx.size)
                    mag_fraction.append(recovered.size / idx.size)
            else:
                mag_mag.append(end_mag)

                if idx.size <= 0:
                    mag_fraction.append(np.nan)
                else:
                    mag_fraction.append(recovered.size / idx.size)

            begin_mag = end_mag
            end_mag = end_mag + size_of_bin
            
        mag_mag, mag_fraction = np.asarray(mag_mag), np.asarray(mag_fraction)
        # Fill in the bins that didn't have any "fraction" and were assigned nan.  Filled with
        # next valid entry.
        mag_fraction = pd.Series(mag_fraction).fillna(method='backfill').values        
        mag_comp = self._interpolateCompMag(mag_mag, mag_fraction, completeness)

        return mag_comp

    def _interpolateCompMag(self, mags, fracs, completeness):
        """
        Linearly extrapolates between the points that bound 0.5. 
        """
        # Make sure that we only get the data from the right half of the graph.
        max_idx = np.argmax(fracs)
        fracs = fracs[max_idx:]
        mags = mags[max_idx:]

        completeness = completeness / 100.0
        idx1 = np.where(fracs <= completeness)[0][0]
        idx2 = np.where(fracs >= completeness)[0][-1]

        x1 = fracs[idx1]
        y1 = mags[idx1]

        x2 = fracs[idx2]
        y2 = mags[idx2]

        dif = abs(y1-y2)
        if dif > 0.5:
            raise ValueError("Interpolating between mags is different by > 0.5 check completeness.")
        
        m = (y2 - y1) / (x2 - x1)
        b = (-m * x1 + y1)

        linear = lambda x: m * x + b
        return linear(completeness)

    def _iterateParameter(self):
        """
        Assumes format of base_XX.(param, fake, phot).
        """
        cd = os.getcwd() + '/'
        files = glob.glob(cd + "parameters_*.param")
        size = len(files)

        nextFile = ""
        if size > 0:
            numbers = [int(files[i].split("_")[1].split(".")[0]) for i in range(len(files))]
            
            numbers = sorted(numbers, key=int)
            nextVal = numbers[-1] + 1

            end = ""
            if nextVal < 10:
                end = "_0%d" % nextVal
            else:
                end = "_%d" % nextVal

            nextFile = "parameters" + end + ".param"
        else:
            nextFile = "parameters_01.param"
        return nextFile

    def _isStringFloat(self, string):
        """
        Pass in a string and trys to convert to float.  If it fails it will return False else True.
        """
        try:
            float(string)
            return True
        except ValueError:
            return False

class GetMagError(Exception):
    """This is raised when the min/max mags are to be found without the passed in files.
    """
    def __init__(self, message):
        super(GetMagError, self).__init__(message)

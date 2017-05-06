#!/astro/apps6/annaconda/bin/python2

"""
This file contains all the user specific parameters that can be changed to customize the Server and other aspects
to their liking.
"""

import multiprocessing
import getpass
import os

####
#CORE_COUNT = multiprocessing.cpu_count() # How many threads will run commands (runningCommands = CORE_COUNT-1)
CORE_COUNT = 0
MAX_CONDOR_SIZE = 3000 # This will be the max size of the queued jobs in condor
CONDOR_ON = True # Changes this to False if you don't want to use condor
#USER_ID = getpass.getuser() # This will keep track of the user id
PORT_NUMBER = 42424 # Change this if somebody else is using the same port
HOST_IP_ADDRESS = "10.155.88.139" # Change to IP address that your server is running on.  Currently set to Eagle.
MATCH_SERVER_DIR = "/astro/users/tjhillis/M83/MatchExecuter" # This sets the path to the MatchServer directory. Missing forward slash on purpose.
MATCH_EXECUTABLE_BIN = "/astro/apps7/opt/match2.7/bin/" # Change this to the disired match install. Forward slash on purpose.
####

#MATCH_SERVER_DIR = "/home/tristan/BenResearch/executer" # This line is for testing purposes

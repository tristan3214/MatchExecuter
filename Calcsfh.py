#!/astro/users/garofali/anaconda/bin/python2
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os
import signal
import subprocess
import threading
import time

from UserParameters import *

__author__ = "Tristan J. Hillis"

"""
Synopsis
--------
This is where all the pieces to run a fit are built.  That does not mean this is where things are run.  It is rather where one can change the core
attributes of how post-processing is done.  If you want to change what gets passed into a script to be run in the shell you do it here.  Or maybe
if you want to bake in a long running MATCH command that I haven't yet (eg calcsfh) this is the place to do it.

Classes - This will be a basic run down of how these classes interact.
-------
MatchThread : This is where any of the classes are run.  Classes are threaded to run the fits in bash while not blocking.  However,
              there are attributes needed in the thread
"""


####################
# Useful functions #
####################
def findStringInList(s_list, s):
    """
    Takes in a list of strings and returns the index of the found string.
    """
    for i, string in enumerate(s_list):
        if s in string:
            return i
    return None
####################


class MatchThread(threading.Thread):
    """
    This acts like a regular Thread object and is called the same only there are custom class variables.
    """
    def __init__(self, line, target=None, args=(), name=None):
        """
        Initializes Thread the same way just with an additive class variable.
        Takes in a single string line that will be parsed by the target method
        """
        threading.Thread.__init__(self, target=target, args=args, name=name)
        self.cancel = False # This gets set to True if the bash command is to be canceled
        self.command = line # Saves the command sent to this thread
        self.name = name


class ProcessRunner(object):
    """
    This holds the generic running method used by all these objects.
    """
    def __init__(self, command):
        """
        There will always be a command that is initially passed in when an object is created.
        """
        self.curr_command = command

    def run(self):
        """
        This is called to run the current command.  For example, when the object is first made, this is called to run the calcsfh command.
        However, after the variable "self.curr_command" can be changed to something else, and calling this will execute that command.
        """

        # This thread, t, should always be a MatchThread that has the attribute of a cancel variable.  If this cancel
        # is ever changed from False to True then this method will exit.
        t = threading.current_thread()
        
        pipe = subprocess.Popen(self.curr_command, shell=True, preexec_fn=os.setsid)

        # poll the status of the process
        while pipe.poll() is None:
            #print("running sleep")
            # if the thread is to be canceled then this will kill the process.
            if t.cancel:
                print("CANCELED", t.name)
                os.killpg(os.getpgid(pipe.pid), signal.SIGTERM) # kills group of processes when present
                self._cleanup()
                break
            time.sleep(0.5)

    def _cleanup(self):
        """
        Clean up after.  To be filled in when this class is inherited.  Otherwise nothing happens.
        """
        pass


class DefaultCalcsfh(ProcessRunner):
    """
    This encapsulates the general calcsfh run.  This will be extendable to a custom, user made, object if a more complicated
    calcsfh process needs to be run.  Generally this extra complexity will be found in processes after the main calcsfh run.  For example,
    the default zcombine command to run here is "zcombine -bestonly fit_name > fit_name.zc".  A user can inherit this class and manually
    change this command to something more complicated.  There is also a script the user can specfiy that will run at the very end.  An example
    of such a script could be plotting the SFH after the fit completes.
    """
    
    def __init__(self, command):
        """
        calcsfh command is passed in here.  This will parse the command of its attributes and then go to run the main
        calcsfh command.
        """
        # save command initially
        super(DefaultCalcsfh, self).__init__(command)
        self.original = command # this is the original beginning command
        #self.curr_command = command # variable is populated for running in the run() method

        self.zcombine_name = None # initialize
        self.co_file = None # initialize
        self.skip = False
        self.isHybrid = False
        
        command = command.split()
        # Add in the MATCH install
        command[0] = MATCH_EXECUTABLE_BIN + command[0]
        print(command)

        # working directory
        self.cwd = "/".join(command[1].split("/")[:-1]) + "/" # split the first command that has the parameter file and get the cwd
        print(self.cwd)

        # Add 'cd' to the curr_command
        self.curr_command = "cd %s; "%self.cwd + self.curr_command
        
        # parameter file name
        self.parameter = command[1].split("/")[-1]
        print(self.parameter)

        # photometry file
        self.phot = command[2].split("/")[-1]
        print(self.phot)

        # fake file
        self.fake = command[3].split("/")[-1]
        print(self.fake)

        # fit name
        self.fit = command[4].split("/")[-1]
        print(self.fit)

        # cmd file name
        self.cmd_file = self.fit + ".cmd"
        
        # caclsfh output file
        if ">" in command: # in case command doesn't have direction file
            self.co_file = command[-1].split("/")[-1]
            print(self.co_file)
        
        # get flags
        self.flags = command[5:-2] # flags start after the fit name and the end of the command will always direct the calcsfh output
        if "-mcdata" in self.flags:
            self.mcdata = self.fit + ".dat"
        print(self.flags)

        self._getDAv()
        self._checkGroup()
        self._checkForFlags()

    def condorCommands(self):
        """
        Return a list of all the commands that will be run to put into a condor config file.
        """
        forCondor = [self.curr_command]
        self.zcombine()
        forCondor.append(self.curr_command)
        self.processFit()
        forCondor.append(self.curr_command)
        if self._group is not None:
            forCondor.append("group %s %s" % (self._group, self.original))
        return forCondor

    def processFit(self):
        files = [self.cwd+self.parameter, self.cwd+self.phot, self.cwd+self.fake, self.cwd+self.fit,
                 self.cwd+self.co_file, self.cwd+self.zcombine_name, self.cwd+self.cmd_file]
        if not self.isHybrid: # no -mcdata flag
            self.curr_command = "%s/scripts/calcsfh_script.sh %s %s %s %s %s %s %s" % \
                                (MATCH_SERVER_DIR, files[0], files[1], files[2], files[3], files[4], files[5], files[6])
        else: # with -mcdata flag
            self.curr_command = "%s/scripts/hybridMC_script.sh %s %s %s %s %s %s %s %s" % \
                                (MATCH_SERVER_DIR, files[0], files[1], files[2], files[3], files[4], files[5], files[6], self.cwd+self.mcdata)

    def zcombine(self):
        """
        This is where the user can specify the current command for zcombine.  User should overwrite this in inheritance if they need
        to employ something more complex than the default zcombine command
        """
        # set the current command
        self.curr_command = "%szcombine -bestonly %s > %s.zc" % (MATCH_EXECUTABLE_BIN, self.cwd + self.fit, self.cwd + self.fit)
        # set a file name for the new zcombine name
        self.zcombine_name = self.fit + ".zc"
        print(self.zcombine_name)

    def _checkForFlags(self):
        """
        This will check for the custom flag -skip.  "-skip" is used to skip the main fit, ie the first command, and go straight to the 
        zcombine and post-processing scripts.

        This will also check if the -mcdata flag is being used and will change the post-processing accordingly.  Se the processFit method.
        """
        if "-skip" in self.curr_command:
            self.skip = True

        if "-mcdata" in self.curr_command:
            self.isHybrid = True

    def _cleanup(self):
        """
        This is canceled when the process is canceled abruptly, in which the files corresponding to this run
        of calcsfh will be erased.
        """
        files = [self.cwd+self.fit, self.cwd+self.co_file, (self.cwd+self.zcombine_name if self.zcombine_name is not None else None),
                 (self.cwd+self.cmd_file if self.cmd_file is not None else None)]
        for file in files:
            if self._checkFile(file):
                os.remove(file)
        
    def _checkFile(self, file):
        """
        This is used by cleanup to check the exisentce of a file
        """
        if file is not None and os.path.isfile(file):
            return True
        else:
            return False

            
    def _checkGroup(self):
        """
        This will check the flags for a group name and assign it a variable
        """
        self._group = None
        idx = None
        for i, flag in enumerate(self.flags):
            if "-group=" in flag:
                # assign variable with group name
                idx = i
                self._group = flag.split("=")[-1]

        # remove group name from command so that it can run in bash
        if self._group is not None:
            flag_command_idx = findStringInList(self.curr_command.split(), "-group")
            command = self.curr_command.split()
            command.pop(flag_command_idx)
            self.flags.pop(idx)
            self.curr_command = " ".join(command)
    

    def _getDAv(self):
        """
        This will take the flags and process for a dAv
        """
        idx = [i for i, flag in enumerate(self.flags) if "-dAv" in flag]
        try:
            idx = idx[0]
            self.dAv = float(self.flags[idx].split("=")[1])
            print(self.dAv)
        except IndexError:
            pass


class GroupProcess(ProcessRunner):
    """
    This class makes a list of DefaultCalcsfh's and will run a script for them using a path and baseName.
    Note it is up to the user to decide what to do with the path name and baseName.
    """
    def __init__(self, grouping, path, baseName, commands):
        """
        Takes in a path and a baseName and will pass this to a script that will run the appropriate base name.
        """
        # set the current command to run a bash script and pass in the path and baseName to the script
        #calcsfhs = [DefaultCalcsfh(calcsfh) for calcsfh in commands]
        #super(GroupProcess, self).__init__("%s/scripts/group_script.sh %s %s %s %s" % (MATCH_SERVER_DIR, path, baseName,
        #calcsfhs[0].phot, calcsfhs[0].parameter))
        s = "%s/scripts/group_script.sh %s %s \"%s\"" % (MATCH_SERVER_DIR, grouping, path, commands[0])
        for command in commands[1:]:
            s += " \"%s\"" % (command)
        
        #super(GroupProcess, self).__init__("%s/scripts/group_script.sh %s %s %s" % (MATCH_SERVER_DIR, path, baseName, commands))
        super(GroupProcess, self).__init__(s)

class SSPCalcsfh(DefaultCalcsfh):
    """
    This class handles running calcsfh commands that contain the -ssp flag.  This flag makes it so the calcsfh output is a
    large list of fits for a single star within the given parameters like dAv.  The calcsfh output is then put through sspcombine
    to output what a single star would look like given the input CMD.  It is suggested to run the -full flag when using -ssp to avoid
    some weird errors without it.
    """
    def __init__(self, command):
        super(SSPCalcsfh, self).__init__(command)
        # initialize the variable to hold the sspcombine name
        self.sspcombine_name = None
        
    def sspcombine(self):
        self.co_shortened = self.fit + ".so"
        self.curr_command = "tail -n +11 %s > %s; %ssspcombine %s > %s.ssp" % (self.cwd + self.co_file, self.cwd + self.co_shortened, MATCH_EXECUTABLE_BIN,
                                                                             self.cwd + self.co_shortened, self.cwd + self.fit)
        # set a file name for the new zcombine name
        self.sspcombine_name = self.fit + ".ssp"

    def processFit(self):
        files = [self.cwd+self.parameter, self.cwd+self.phot, self.cwd+self.fake, self.cwd+self.fit,
                 self.cwd+self.co_file, self.cwd+self.sspcombine_name, self.cwd+self.cmd_file]
        self.curr_command = "%s/scripts/ssp_script.sh %s %s %s %s %s %s %s" % \
                            (MATCH_SERVER_DIR, files[0], files[1], files[2], files[3], files[4], files[5], files[6])

    def condorCommands(self):
        """
        Return a list of all the commands that will be run to put into a condor config file.
        """
        forCondor = [self.curr_command]
        self.sspcombine()
        forCondor.append(self.curr_command)
        self.processFit()
        forCondor.append(self.curr_command)
        if self._group is not None:
            forCondor.append("group %s %s" % (self._group, self.original))
        return forCondor

    def _cleanup(self):
        """
        This is canceled when the process is canceled abruptly, in which the files corresponding to this run
        of calcsfh will be erased.
        """
        files = [self.cwd+self.fit, self.cwd+self.co_file, (self.cwd+self.sspcombine_name if self.sspcombine_name is not None else None),
                 (self.cwd+self.cmd_file if self.cmd_file is not None else None)]
        for file in files:
            if self._checkFile(file):
                os.remove(file)
                        
class Sleep(ProcessRunner):
    """
    This is a test object.
    """
    def __init__(self, stime):
        """
        The sleep time in seconds is passed in.
        """
        super(Sleep, self).__init__("sleep %s" % stime)
        self.stime = stime # capture thread time

    def afterSleep(self):
        self.curr_command = "./sleep_script.sh"
        
    def _cleanup(self):
        print("Cleaning up after sleep")

        
def main():
    """
    This is only used for testing purposes
    """
    list = ["calcsfh locke command", "calcsfh second command", "fake stuff"]

    group = GroupProcess("/home/tristan/BenResearch/executer/scripts", "stuff", list)
    group.run()

if __name__ == "__main__":
    main()

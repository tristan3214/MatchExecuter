#!/astro/apps6/anaconda/bin/python2
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import getpass
import multiprocessing
import os
from Queue import Queue
import signal
import subprocess
import sys
import thread
import threading
import time

from twisted.protocols import basic
from twisted.internet import protocol, reactor
from threading import Thread

from UserParameters import *
import MyLogger
from Calcsfh import DefaultCalcsfh
from Calcsfh import GroupProcess
from Calcsfh import MatchThread
from Calcsfh import Sleep
from Calcsfh import SSPCalcsfh

"""
This server runs on port 42424
"""

# These have been moved to UserParameters.py
# Global Variables
#CORE_COUNT = multiprocessing.cpu_count()
#CORE_COUNT = 15
#MAX_CONDOR_SIZE = 3000 # this controlls the maximum size of a condor run
#CONDOR_ON = True

workQueue = Queue()
activeThreads = {} # this should only every be one more larger than the number of CPUs on the system.
                   # main thread handles incoming data and one thread waits on events and the other threads
                   # execute the bash commands.
dAvRangeThreads = {}
dAvRangeGroup = {} # dictionary that holds a dictionary of commands
doneThreads = Queue()

# Events for watchdogs
watcherEvent = threading.Event() # a single thread waits for set to join a certain thread
condorEvent = threading.Event() # activates the condor thread

log = MyLogger.myLogger("MatchServer", "server")

def getThreadNumber():
    print(activeThreads)
    num = None
    if len(activeThreads) == 0: # no threads yet
        num = '1'
    else: # get the thread number that is missing in the range of 1 to 8
        keys = activeThreads.keys()
        print(keys)
        keys = map(int, keys)
        keys = sorted(keys, key=int)
        print(keys)
        count = 1
        for name in keys:
            if count == name:
                count += 1 
            else:
                break
        num = count
    return num

def getdAvName():
    print(dAvRangeThreads)
    num = None
    grouped = dAvRangeGroup.keys()
    grouped = [key for key in grouped if "dAv" in key]
    if len(dAvRangeThreads) == 0 and len(grouped) == 0: # no threads yet
        num = '1'
    else: # get the thread number that is missing in the range of 1 to 8
        keys = []
        if len(dAvRangeThreads) != 0:
            keys += dAvRangeThreads.keys()
        if len(grouped) != 0:
            keys += grouped
        
        keys = [key.split("_")[-1] for key in keys]
        print(keys)
        keys = map(int, keys)
        keys = sorted(keys, key=int)
        print(keys)
        count = 1
        for name in keys:
            if count == name:
                count += 1 
            else:
                break
        num = count
    return int(num)

class MatchExecuter(basic.LineReceiver):
    """
    Class description
    """
    def connectionMade(self):
        """
        Method desc.
        """
        self.sendLine("Welcome to MATCH executer")
        self.factory.clients.append(self)

    def connectionLost(self, reason):
        """
        Method desc.
        """
        self.factory.clients.remove(self)

    def lineReceived(self, line):
        """
        Method desc.
        """
        log.info("Received:" +  line)
        input = line.split(" ")
        # If there are enough open threads then assign a command
        if len(activeThreads) + 1 <= CORE_COUNT or input[0] == "cancel" or input[0] == "show" or "-dAvrange" in line or input[0] == "group": 
            cp = CommandParser()
            data = cp.parse(line)
            if data is not None:
                self.sendData(data)
        else: # If all processes are used put received line in a work Queue
            condorEvent.set()
            condorEvent.clear()
            log.info("All threads taking adding command to queue - " + line)
            workQueue.put(line) 
        
    def sendData(self, data):
        """
        Decorator method to self.sendMessage(...) so that it
        sends the resulting data to every connected client.
        """
        if data is not None:
            self.sendMessage(str(data))

    def sendMessage(self, message):
        """
        Sends message to every connect client.
        """
        for client in self.factory.clients:
            client.sendLine(message)


class MatchExecuterFactory(protocol.ServerFactory):
    """
    Statement
    """
    protocol = MatchExecuter
    clients = []


class CommandParser(object):
    def __init__(self):
        self.commands = CommandMethods()
        
    def parse(self, input=None):
        """
        Input must start with a keyword argument. For example, if the user wants to
        cancel a command then they must have the "cancel" key followed by the Matching command.
        """
        line = input
        input = input.split(" ")
        print("Split input:", input)
        
        if input[0] == "calcsfh":
            # find the best dAv but can also pass in lower and upper bounds with a step (e.g. -dAvrange=0.0,1.0,0.1)
            if "-dAvrange" in line:
                # get attributes
                dAv = ""
                for i, arg in enumerate(input):
                    if "-dAvrange" in arg:
                        dAv = arg

                dAv = dAv.split("=")[1].split(",")
                lower = float(dAv[0])
                upper = float(dAv[1])
                step = float(dAv[2])

                log.info("generating dAv commands in the specified range with step - " + line)
                
                t = MatchThread(line, target=self.commands.dAvRange, args=(line, lower, upper, step), name="dAv_%d"%getdAvName())
                dAvRangeThreads[t.name] = t
                t.start()

            else:
                log.info("run calcsfh command - " + line)
                startCommand(line, self.commands.calcsfh, (line,), name=getThreadNumber())
            return None
        
        if input[0] == "group":
            groupName = input[1]
            command = " ".join(input[2:])
            print("GROUP COMMANDS:", dAvRangeGroup[groupName])
            print(groupName, command)
            dAvRangeGroup[groupName][command] = True
            startCommand(None, runGroup, (dAvRangeGroup[groupName],), name=getThreadNumber())
            runGroup(dAvRangeGroup[groupName])

        if input[0] == "cancel":
            if input[1] == "all":
                self.commands.clearAll()
            else:
                line = " ".join(input[1:])
                self.commands.cancel(line)
                log.info("canceling command - " + line)
            return None

        if input[0] == "show":
            line = self.commands.show(input)
            return line

        # sleep for testing object based MatchExecuter
        if input[0] == "sleep":
            print("starting object sleep thread")
            log.info("starting object sleep thread")

            startCommand(line, self.commands.sleep2, (input[1],), name=getThreadNumber())
            return None
            
        # for testing purposes
        """
        if input[0] == "sleep":
            log.info("starting sleep thread")
            t = MatchThread(line, target=self.commands.sleep, args=(input[1],), name=getThreadNumber())
            activeThreads[t.name] = t
            t.start()
            return None
        """

def startCommand(line, method, args, name):
    t = MatchThread(line, target=method, args=args, name=name)
    activeThreads[t.name] = t
    t.start()
    
class CommandMethods(object):
    """
    This method executes the commands that are sent to this server.  Examples include calcsfh and the find best
    dAv script.
    """
    def __init__(self):
        pass

    def calcsfh(self, line):
        if "-ssp" not in line:
            calcsfh = DefaultCalcsfh(line)
            if not calcsfh.skip:
                # run the initial command
                calcsfh.run()
                
            # run zcombine at the end
            calcsfh.zcombine()
            calcsfh.run()

            # process calcsfh files after
            calcsfh.processFit()
            calcsfh.run()
            
        else: # SSP run
            calcsfh = SSPCalcsfh(line)
            if not calcsfh.skip:
                # Run the initial command
                calcsfh.run()

            # run sspcombine
            calcsfh.sspcombine()
            calcsfh.run()

            # process ssp files after
            calcsfh.processFit()
            calcsfh.run()
            
        # check for group and run if it is the last one in the group
        if calcsfh._group is not None:
            dAvRangeGroup[calcsfh._group][calcsfh.original] = True
            self.runGroup(dAvRangeGroup[calcsfh._group])
            
        # cleanup the thread that is done
        cleanupThread(doneThreads)

    def dAvRange(self, line, lower=0.0, upper=1.0, step=0.2):
        """
        This method takes in a calcsfh command along with the custom -dAvRange and makes several calcsfh commands
        that will comprise of the total dAv range.  These commands are added to the queue for later.
        """
        t = threading.current_thread()

        # There may be a 'cd' at the beginning edit for this change
        cd = None
        if "cd" == line[:2]:
            cd = " ".join(line.split()[:2])
            line = line.split()[2:]
        else:
            line = line.split()
            
        numSteps = int((upper - lower) / step) + 1 # will underestimate by one so I add one

        commands = [] # list of commands to be added to queue

        currentDaV = lower
        for i in xrange(numSteps):
            newLine = list(line)
            for j, arg in enumerate(line):
                if "-dAvrange" in arg:
                    # add the dAv in 
                    newLine[j] = "-dAv=%.3f" % currentDaV
                    # put in new file names
                    args = list(line)

                    name = args[4].split("/")
                    name[-1] += ("_dAv_%.2f" % currentDaV).replace(".", "-")
                    name = "/".join(name)
                    newLine[4] = name

                    output = args[-1].split("/")
                    outputName = output[-1].split(".")
                    outputName[0] += ("_dAv_%.2f" % currentDaV).replace(".", "-")
                    outputName = ".".join(outputName)
                    output[-1] = outputName
                    output = "/".join(output)
                    newLine[-1] = output

                    # put in a custom flag called -group=groupName
                    newLine.insert(-2, "-group=%s" % (t.name))
                    

            if cd is not None:
                commands.append("%s %s" % (cd, " ".join(newLine)))
            else:
                commands.append(" ".join(newLine))

            print(newLine)
            print(commands[i])
            print()
            currentDaV += step

        dAvRangeGroup[t.name] = {} # add a dictionary 
            
        for command in commands:
            dAvRangeGroup[t.name][command] = False # add that this command is not done
            workQueue.put(command)
            #print(command)

        t.cancel = True
        doneThreads.put(dAvRangeThreads.pop(t.name))

        condorEvent.set()
        condorEvent.clear()
        
        watcherEvent.set()
        watcherEvent.clear()

    def show(self, input):
        try:
            input[1] # test if there is another key
            if input[1] == "queue":
                size = workQueue.qsize()
                line = ""
                # show all the commands from the queue
                if size > 0:
                    tempQ = Queue()
                    # get and print all queue commands
                    for i in range(size):
                        command = workQueue.get()
                        line += command + "\n"
                        tempQ.put(command)
                    # requeue commands
                    for i in range(size):
                        workQueue.put(tempQ.get())
                else:
                    line += "no queued commands"
                return line
            if input[1] == "threads":
                # show all the commands being run on active threads
                keys = activeThreads.keys()
                line = ""
                if len(keys) > 0:
                    for key in keys:
                        t = activeThreads[key]
                        line += t.command + "\n"
                else:
                    line += "no current threads running"
                return line
            if input[1] == "number":
                count = len(activeThreads) + workQueue.qsize()
                line = "Process to run: " + str(count)
                return line
        except IndexError:
            # show all commands in queue and in thread
            line = ""
            size = workQueue.qsize()
            # show all the commands from the queue
            if size > 0:
                tempQ = Queue()
                # get and print all queue commands
                for i in range(size):
                    command = workQueue.get()
                    line += command + "\n"
                    tempQ.put(command)
                # requeue commands
                for i in range(size):
                    workQueue.put(tempQ.get())

            keys = activeThreads.keys()
            if len(keys) > 0:
                for key in keys:
                    t = activeThreads[key]
                    line += t.command + "\n"

            if line == "":
                return "no commands to show"
            else:
                return line

    def runGroup(self, dictionary):
        """
        Passed in is a list of commands belonging to a group of commands.
        This method will run a script to process these grouped fits.
        """
        # check if all the commands in the dictionary are set to true
        done = dictionary.values()
        if all(bool is True for bool in done) is True:
            ## run code on group
            # isolate working directory
            print("DONE:", done)
            keys = dictionary.keys()
            #print("KEYS:", keys[0])
            workingD = keys[0].split(" ")
            workingD = workingD[4].split("/")[:-1]
            workingD = "/".join(workingD) + "/"
            print("WORKING DIRECTORY:", workingD)

            # isolate base name
            baseName = keys[1].split(" ")
            baseName = baseName[4].split("/")[-1]
            baseName = baseName.split("_")
            baseName = "_".join(baseName[:-2])
            print("BASE NAME:", baseName)

            group = GroupProcess('bestdAv', workingD, baseName, keys)
            group.run()
        else:
            # do nothing to group
            print("CURRENTLY DONE:", done)
        pass

        
    def sleep(self, stime):
        """
        Testing command by running a script that sleeps a process.
        """
        t = threading.current_thread()
        
        pipe = subprocess.Popen("./sleep.sh %s" % stime, shell=True, preexec_fn=os.setsid)
        
        while pipe.poll() is None:
            if t.cancel:
                os.killpg(os.getpgid(pipe.pid), signal.SIGTERM) # kills group of processes when present
                break
            time.sleep(0.5) # add sleep so this isn't as intensive
            
        t.cancel = True # says this thread is ready to be joined and removed from the dictionary
        doneThreads.put(activeThreads.pop(t.name))
        
        watcherEvent.set()
        watcherEvent.clear()

    def sleep2(self, stime):
        """
        Testing command for running object oriented MatchExecuter.
        """
        sleepObj = Sleep(stime)
        sleepObj.run()

        print("Done sleeping")
        time.sleep(0.5)
        sleepObj.afterSleep()
        sleepObj.run()

        cleanupThread(doneThreads)
        
    def clearAll(self):
        """
        This method, when called, will clear all the commands to be run in the queue as well as the threads.
        """
    
        if workQueue.qsize() > 0:
            # empty queue
            size = workQueue.qsize()
            for i in range(size):
                workQueue.get()
                
        for key in activeThreads:
            # cancel all the threads
            t = activeThreads[key]
            t.cancel = True
    
        return
        
    def cancel(self, line):
        """
        Matches the sent line to the internally set thread variable command.  If the same
        it will set this to cancel
        TODO: Add cleanup of files for the command that is being canceled. Calcsfh's have predictable pattern
        for grabing the fit name.
        """

        for key in activeThreads:
            t = activeThreads[key]
            if line == t.command:
                log.info("Canceled command in running thread (%s)" % line)
                t.cancel = True
                return
            
        if workQueue.qsize() > 0:
            # empty queue into temporary one and check for the right command to get rid of.
            # at end put tempQ commands back into the workQueue
            tempQ = Queue()
            size = workQueue.qsize()
            for i in range(size):
                command = workQueue.get()
                print(command)
                if line == command:
                    log.info("Canceled command in queue (%s)" % line)
                else:
                    tempQ.put(command)
            size = tempQ.qsize()
            
            # refill work queue
            for i in range(size):
                print(command)
                workQueue.put(tempQ.get())
            return

        # if a return was not reached then there was no similarly found command
        log.info("Couldn't find command to cancel (%s)" % line)

def runGroup(dictionary):
    """
    Passed in is a list of commands belonging to a group of commands.
    This method will run a script to process these grouped fits.
    """
    # check if all the commands in the dictionary are set to true
    done = dictionary.values()
    if all(bool is True for bool in done) is True:
        ## run code on group
        # isolate working directory
        print("DONE:", done)
        keys = dictionary.keys()
        #print("KEYS:", keys[0])
        workingD = keys[0].split(" ")
        workingD = workingD[4].split("/")[:-1]
        workingD = "/".join(workingD) + "/"
        print("WORKING DIRECTORY:", workingD)

        # isolate base name
        baseName = keys[1].split(" ")
        baseName = baseName[4].split("/")[-1]
        baseName = baseName.split("_")
        baseName = "_".join(baseName[:-2])
        print("BASE NAME:", baseName)

        group = GroupProcess('bestdAv', workingD, baseName, keys)
        group.run()
    else:
        # do nothing to group
        print("CURRENTLY DONE:", done)
        pass

def cleanupThread(threadQueue):
    """
    Passed in thread must be MatchThread
    """
    t = threading.current_thread()
    t.cancel = True

    threadQueue.put(activeThreads.pop(t.name))

    watcherEvent.set()
    watcherEvent.clear()
        
def stripCalcsfh(line):
    """
    This takes a calcsfh command line and will strip away the directory information and return
    a less verbose version.  The command that is returned will only run in the respective directory
    when calling calcsfh.
    """
    line = line.split()

    # first entry is parameter file
    line[1] = line[1].split("/")[-1]
    # second entry is photometry file
    line[2] = line[2].split("/")[-1]
    # third entry is fake file
    line[3] = line[3].split("/")[-1]
    # fourth entry is fit name
    line[4] = line[4].split("/")[-1]
    # last entry is output file name
    line[-1] = line[-1].split("/")[-1]

    return " ".join(line)

def emptyQueue(queue):
    size = queue.qsize()
    for i in xrange(size):
        queue.get()


class CondorWatcher(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        currentSize = 0
        while True:
            print("CONDOR WAITING")
            if currentSize == 0:
                condorEvent.wait()
            print("CONDOR NOT WAITING")
            currentSize = workQueue.qsize()
            print("SIZE:", currentSize)
            while True:
                time.sleep(1)
                newSize = workQueue.qsize()
                if newSize - currentSize != 0:
                    currentSize = workQueue.qsize()
                    print("QUEUE SIZE CHANGING")
                else:
                    print("QUEUE SIZE CONSTANT")
                    break
            # when things are added to queue but all are run by thread this will continue the condor thread to wait.
            if currentSize == 0:
                continue
            # grab commands from queue and make a list of sfh objects
            commands = self.makeCommandList()
            print(commands)
            # write config file
            self.makeCondorConfig(commands)
            print("STARTING CONDOR")
            self.runCondor()

            # wait for job to end
            while self.condorRunning():
                time.sleep(300)
                print("JOBS STILL RUNNING")
            currentSize = workQueue.qsize()
            
    ### Put condor_thread_watcher methods here
    def filterCommand(self, command):
        """
        Takes in a command a command as a string.  Splits it up and parses it 
        to feed it to the right, associated, object.
        """
        command_list = command.split()
        if command_list[0] == "calcsfh":
            if "-ssp" in command_list:
                return SSPCalcsfh(command)
            
            return DefaultCalcsfh(command)
    
    def makeCommandList(self):
        commands = []
        size = workQueue.qsize()
        stop = 0
        if size < MAX_CONDOR_SIZE:
            stop = size
        else:
            stop = MAX_CONDOR_SIZE
        for i in range(stop):
            commands.append(self.filterCommand(workQueue.get()))

        return commands

    def makeCondorConfig(self, commands):
        f = open("jobs.cfg", 'w') # create config file in the ServerMatch directory
        self.to_job_config = MATCH_SERVER_DIR + "/jobs.cfg"
        # write condor config header information
        f.write("Notification = never\n")
        f.write("getenv = true\n")
        f.write("Executable = %s/scripts/condor_script.sh\n" % MATCH_SERVER_DIR)
        f.write("Initialdir = %s/scripts/\n" % MATCH_SERVER_DIR)
        f.write("Universe = vanilla\n\n")

        # write commands as queued jobs
        for i, job in enumerate(commands):
            f.write("Log = /dev/null\n")
            f.write("Output = /dev/null\n")
            f.write("Error = /dev/null\n")
            #f.write("Log = /astro/users/tjhillis/M83/test.log\n")
            #f.write("Output = /astro/users/tjhillis/M83/test.out\n")
            #f.write("Error = /astro/users/tjhillis/M83/test.err\n")
            # string of commands
            analysis = job.condorCommands()
            analysis = " | ".join(analysis)
            f.write("Arguments = \"%s\"\n" % analysis)
            f.write("Queue\n\n")

        f.close()

    def runCondor(self):
        ssh = subprocess.Popen('ssh -xtt condor', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        ssh.stdin.write("condor_submit %s\n" % self.to_job_config)
        ssh.stdin.write("condor_q -sub %s\n" % getpass.getuser())
        ssh.stdin.write("exit\n")
        ssh.stdin.close()
        ssh.wait()

        lines = ssh.stdout.readlines()
        lines = [line.rstrip() for line in lines]
        for line in lines:
            print(line)

    def condorRunning(self):
        """
        Checks to see if there is still jobs and returns True if there is.
        """
        ssh = subprocess.Popen('ssh -xtt condor', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        ssh.stdin.write("condor_q -sub %s\n" % getpass.getuser())
        ssh.stdin.write("exit\n")
        ssh.stdin.close()
        ssh.wait()

        lines = ssh.stdout.readlines()
        lines = [line.rstrip() for line in lines]
        status = int(lines[-3][0])

        if status == 0:
            return False
        else:
            return True

def threadWatcher():
    """
    This method waits for a thread to set an event and will then join that thread.  An example of
    such an event is sending a command for the thread to be canceled or if the thread encounters an error.
    """
    while True:
        print("WAITING")
        watcherEvent.wait()

        log.info("Thread finished starting more processes")
        print("TRIGGERED THREAD WATCHER")
        # find thread that activated event using "cancel" internal boolean
        size = doneThreads.qsize()

        print("ACTIVE THREADS:", activeThreads)
        for i in xrange(size):            
            t = doneThreads.get()
            # join thread
            t.join()

            print("THREAD NAME:", t.name)
            # Start all the dAv commands that were fed to queue as long as there are
            # threads open.
            if "dAv" in t.name: # if the name is None then it is a run that used dAvrange
                activeCount = len(activeThreads)
                left = CORE_COUNT - activeCount
                print("CORES LEFT", left)
                if left > 0:
                    workSize = workQueue.qsize()
                    if workSize > left:
                        for j in xrange(left):
                            cp = CommandParser()
                            cp.parse(workQueue.get())
                            print("Queue is large: Parsing dAv line")
                    else:
                        for j in xrange(workSize):
                            cp = CommandParser()
                            cp.parse(workQueue.get())
                            print("Queue is small: Parsing dAv line")
                continue
            
            # if something is in the work queue set another thread to the task
            if workQueue.qsize() > 0:
                print(workQueue)
                cp = CommandParser()
                cp.parse(workQueue.get())

        print("BACK TO WAITING")
                
if __name__ == "__main__":
    # Check if we are running from the executable directory
    if MATCH_SERVER_DIR != os.getcwd() + "/":
        os.chdir(MATCH_SERVER_DIR)
    print(os.getcwd())

    watcher = Thread(target=threadWatcher, name="watcher")
    watcher.daemon = True
    watcher.start()

    if CONDOR_ON:
        condor_watcher_thread = CondorWatcher()
        condor_watcher_thread.daemon = True
        condor_watcher_thread.start()

    reactor.listenTCP(PORT_NUMBER, MatchExecuterFactory())
    reactor.run()

#!/astro/users/garofali/anaconda/bin/python2
from __future__ import print_function, division

import sys
import telnetlib
import threading
import time

from UserParameters import *
HOST = HOST_IP_ADDRESS
#HOST = "10.155.88.135" # astrolab18
PORT = PORT_NUMBER

def main():
    tn = telnetlib.Telnet(HOST, PORT)

    # start take commands method
    t = threading.Thread(target=takeCommands, args=(tn,))
    t.daemon = True
    t.start()

    # any incoming data will be printed
    while True:
        msg = tn.read_very_eager()
        if msg != "":
            print(msg)
        time.sleep(1)


def printAll(tn):
    print(tn.read_all())

def takeCommands(tn):
    while True:
        command = raw_input()
        tn.write(command + "\r\n") # twisted server appears to need the \r\n at the end

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(0)

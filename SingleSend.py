#!/astro/users/tjhillis/anaconda2/bin/python2
from __future__ import print_function, division

import sys
import telnetlib
import time

HOST = "10.155.88.139"
PORT = 42424

def main():
    tn = telnetlib.Telnet(HOST, PORT)

    # start take commands method
    send = sys.argv[1:]

    tn.write(send + "\r\n")

    time.sleep(1)

    print(tn.read_very_eager())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(0)


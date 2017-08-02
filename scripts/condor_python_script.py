#!/usr/bin/env python
from __future__ import print_function, division, absolute_import

import subprocess
import telnetlib
import sys

#stdout = sys.stdout
#sys.stdout = StringIO.StringIO()
commands = " ".join(sys.argv[1:])
commands = commands.split("|")
commands = [command.split() for command in commands]
print(commands[0])
print()
print(commands[1])
for command in commands:
    print(command[-1])
redirects = []
for command in commands:
    if "group" in command:
        redirects.append(None)
    elif ">" in command and "group" not in command:
        redirects.append(command[-1])
    else:
        redirects.append(None)
#redirects = [None if command[0] is "group" else command[-1] if ">" in command else None for command in commands]
print()
print(redirects)
commands = [" ".join(command) for command in commands]
print()
print(commands)
for i, redirect in enumerate(redirects):
    if redirect is not None:
        command = " ".join(commands[i].split()[:-2])
        f = open(redirect, 'w')
        subprocess.call(command, stdout=f, shell=True)
        f.close()
    else:

        firstArg = commands[i].split()[0]
        print("FIRST ARGUEMENT:", firstArg)
        if firstArg == "group":
            HOST = "10.155.88.139" # eagle
            PORT = 42424

            tn = telnetlib.Telnet(HOST, PORT)
            tn.write(commands[i] + "\r\n") # twisted server appears to need the \r\n at the end; write to port
            tn.close()
        else:
            subprocess.call(commands[i], shell=True)

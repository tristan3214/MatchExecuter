#!/astro/users/garofali/anaconda/bin/python2
from __future__ import print_function
from __future__ import division

from twisted.internet import defer, protocol, reactor, threads
from twisted.protocols import basic
from twisted.python import log

import thread
import time

def main():
    
    factory = LineClient()
    reactor.connectTCP("localhost", 42424, factory)

    thread.start_new_thread(send, (factory,))
    
    reactor.run()

def send(f):
    time.sleep(1)
    f.protocol.sendCommand("sleep 10")


class LineForwarder(basic.LineReceiver):
    """
    Sends and receives data from Evora server.
    """
    def __init__(self):
        self.output = None
        self._deferreds = {}

    def dataReceived(self, data):
        """
        Handles incoming data and starts the proper call back chain based on the key received from the server.
        """
        pass
        
    def sendCommand(self, data):
        """
        Wrapper method for sending lines to the Evora server.
        """
        self.sendLine(data)
        d = self._deferreds[data.split(" ")[0]] = defer.Deferred()
        return d

    def connectionMade(self):
        """
        Executes when twisted connects to server.
        """
        pass

    def addDeferred(self, string):
        """
        This is used for creating deferred objects when expecting to receive data.
        """
        d = self._deferreds[string] = defer.Deferred()
        return d

    def removeDeferred(self, string):
        """
        Used to get rid of any trailing deferred obejcts (e.g. realSent after an abort)
        """
        if(string in self._deferreds):
            self._deferreds.pop(string)

    def connectionLost(self, reason):
        """
        Executes when connection is lost to Evora server.
        """
        ## Add a "callback" that will close down the gui functionality when camera connection is closed.
        #gui = self.factory.gui
        #gui.onDisconnectCallback()
        pass


class LineClient(protocol.ClientFactory):
    """
    Makes a client instance for the the user running the GUI.
    """
    def __init__(self):
        self.protocol = LineForwarder

    def clientConnectionLost(self, transport, reason):
        """
        Called when client connection is lost normally.
        """
        pass
    
    def clientConnectionFailed(self, transport, reason):
        """
        Called when client connection is lost unexpectedly.
        """
        pass

    
if __name__ == "__main__":
    main()

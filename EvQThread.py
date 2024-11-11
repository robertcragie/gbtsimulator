###############################################################################
#
# MODULE:             GBT Simulator Application
#
# AUTHOR:             Robert Cragie
#
# DESCRIPTION:        Event Queue thread class
#
###############################################################################
#
#  Copyright (c) 2024 Gridmerge Ltd. All Rights Reserved.
#
###############################################################################

from BaseThread import *
from queue import Queue

###############################################################################
# Class : cEvQThread
#
# Worker thread
#
# Thread spawned to do blocking call to obtain event from associated Queue and
# then call virtual method to handle the event.
###############################################################################

class cEvQThread(cBaseThread):
    '''
    Event Queue Thread class. Provides a thread of execution which will
    perform a blocking wait on a single queue then passed the obtained
    event to the HandleEvent() method implemented in a derived class.
    '''

    # Constructor
    def __init__(self):
        cBaseThread.__init__(self)
        # Queue
        self.oQueue = Queue(0)

    # Methods
    def SendEvent(self, event):
        '''
        Put an event to the thread queue.
        '''
        # Put an event to the Queue
        self.oQueue.put(event)

    # Overridden Virtual methods
    def StopUnblock(self):
        '''
        Unblocks the thread blocking on a queue read.
        '''
        # Put a dummy event to the Queue to unblock it
        self.oQueue.put('')

    # Overridden Virtual methods
    def Stop(self):
        cBaseThread.Stop(self)
 
    def Run(self):
        '''
        Thread main loop.
        '''
        while self.bLooping:
            event = self.oQueue.get()
            # Handle event
            if self.bLooping:
                self.HandleEvent(event)
        self.bRunning = False
        # print('cEvQThread exited')

    # Pure Virtual methods to be overridden by derivatives
    # def HandleEvent(self, event):
        # Pure virtual method to handle the event obtained from
        # the queue.

###############################################################################
# Function : EvQThreadMain
#
# Main function. Used for test if module
###############################################################################

def EvQThreadMain():
    pass

if __name__ == '__main__':
    EvQThreadMain()

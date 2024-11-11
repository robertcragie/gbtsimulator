###############################################################################
#
# MODULE:             GBT Simulator Application
#
# AUTHOR:             Robert Cragie
#
# DESCRIPTION:        Base thread class
#
###############################################################################
#
#  Copyright (c) 2024 Gridmerge Ltd. All Rights Reserved.
#
###############################################################################

from threading import *

###############################################################################
# Class : cBaseThread
#
# Worker thread wrapper around basic thread
#
###############################################################################

class cBaseThread:
    '''
    Base Thread class. Provides a thread of execution. Other methods must
    be added in derived classes depending on what the thread does.
    which will block. All derived classes must implement at the very least a
    Run method.
    '''

    # Constructor
    def __init__(self):
        # Thread object
        #print('Creating thread')
        #print(self)
        self.oThread = Thread(target=self.Run)

    # Methods
    def Start(self):
        '''Start new instance of thread'''
        self.bLooping = self.bRunning = 1
        self.oThread.start()

    def Stop(self):
        '''Stop thread'''
        #print('Stopping thread')
        #print(self)
        # Will cause loop to end, dropping out of callable object
        self.bLooping = 0

        # Call unblocking method to cause thread to run
        self.StopUnblock()

        # Wait until worker thread has terminated
        self.oThread.join()

    def IsRunning(self):
        '''Returns whether thread is running or not'''
        return self.oThread.isAlive()

    # Pure Virtual methods to be overridden by derivatives
    # def StopUnblock(self):
        # Method of unblocking any blocking action in the main thread

    # def Run(self):
        # Main thread routine. Should run forever until legitimate
        # terminating condition. Use the control variable self.bLooping

###############################################################################
# Function : BaseThreadMain
#
# Main function. Used for test if module
###############################################################################

def BaseThreadMain():
    pass

if __name__ == '__main__':
    BaseThreadMain()

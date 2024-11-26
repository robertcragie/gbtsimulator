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
# SPDX-License-Identifier: Apache-2.0
#
# Copyright 2024 Gridmerge Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################

from BaseThread import *
from queue import SimpleQueue

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
        self.oQueue = SimpleQueue()

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

###############################################################################
#
# MODULE:             GBT Simulator Application
#
# AUTHOR:             Robert Cragie
#
# DESCRIPTION:        GBT Client Thread
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

import GBT
import Logger

###############################################################################
# Class : cGBTClientThread
#
# GBT client worker thread
###############################################################################

class cGBTClientThread(GBT.cGBTThread):
    '''
    GBT Client Thread class. Provides a thread of execution for
    handling events relevant to the GBT Client operation.
    '''

    # Constructor
    def __init__(self):
        GBT.cGBTThread.__init__(self, GBT.GBT_CLT_BTS, GBT.GBT_CLT_BTW, True)
        self.bTimerEnabled = True # OVERRIDE
        self.oThread.name = "Client Thread"

    def InvokeAccessRequest(self, data):
        '''
        Invoke an ACCESS.request.
        '''
        self.oLoggerThread.PostLog(Logger.LOG_CONSOLE_PRINT, "Invoking ACCESS.request")
        self.StartGBT()
        self.FillSQ(data)
        self.SendGBTAPDUStream()

    def DropMsgFromServer(self, apdu:GBT.cGBTAPDU):
        '''
        Drop a message from the Server task.
        '''
        self.oLoggerThread.PostLog(Logger.LOG_BOTH_PRINT, self.GetApduStr(apdu, True))

    def HandleMsgFromServer(self, apdu:GBT.cGBTAPDU):
        '''
        Handle a message from the Server task.
        '''
        self.oLoggerThread.PostLog(Logger.LOG_BOTH_PRINT, self.GetApduStr(apdu, False))
        # If we are not processing and the incoming APDU has payload, start processing
        if not self.bGBTProcessing:
            if (apdu.BD != None):
                self.oLoggerThread.PostLog(Logger.LOG_CONSOLE_PRINT, "New stream from server")
                # Let's get going
                self.StartGBT()
        self.ProcessGBTAPDU(apdu)

    def HandleEvent(self, event):
        '''
        Pure virtual method to handle the event obtained from the queue.
        '''
        if event.evtType == GBT.EVT_PEER_MSG:
            if self.msgCount in GBT.aCltDropMsgs:
                self.DropMsgFromServer(event.data)
            else:
                self.HandleMsgFromServer(event.data)
            self.msgCount += 1
        elif event.evtType == GBT.EVT_CLT_INVOKE_ACC_REQ:
            self.InvokeAccessRequest(event.data)
        elif event.evtType == GBT.EVT_TIMER_EXPIRY_MSG:
            self.oLoggerThread.PostLog(Logger.LOG_CONSOLE_PRINT, "Client timer expired")
            self.CheckRQandFillGaps()

###############################################################################
# Function : GBTClientThreadMain
#
# Main function. Used for test if module
###############################################################################

def GBTClientThreadMain():
    pass

if __name__ == '__main__':
    GBTClientThreadMain()

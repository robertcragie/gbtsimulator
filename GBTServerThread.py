###############################################################################
#
# MODULE:             GBT Simulator Application
#
# AUTHOR:             Robert Cragie
#
# DESCRIPTION:        GBT Server Thread
#
###############################################################################
#
#  Copyright (c) 2024 Gridmerge Ltd. All Rights Reserved.
#
###############################################################################

import GBT
import Logger

###############################################################################
# Class : cGBTServerThread
#
# GBT server worker thread
###############################################################################

class cGBTServerThread(GBT.cGBTThread):
    '''
    GBT Server Thread class. Provides a thread of execution for
    handling events relevant to the GBT Server operation.
    '''

    # Constructor
    def __init__(self):
        GBT.cGBTThread.__init__(self, GBT.GBT_SVR_BTS, GBT.GBT_SVR_BTW, False)
        self.bTimerEnabled = False # OVERRIDE
        self.oThread.name = "Server Thread"

    def InvokeAccessResponse(self, data):
        '''
        Invoke an ACCESS.response.
        '''
        self.oLoggerThread.PostLog(Logger.LOG_CONSOLE_PRINT, "Invoking ACCESS.response")
        self.StartGBT()
        self.FillSQ(data)
        self.SendGBTAPDUStream()

    def DropMsgFromClient(self, apdu:GBT.cGBTAPDU):
        '''
        Drop a message from the Client task.
        '''
        self.oLoggerThread.PostLog(Logger.LOG_BOTH_PRINT, self.GetApduStr(apdu, True))

    def HandleMsgFromClient(self, apdu:GBT.cGBTAPDU):
        '''
        Handle a message from the Client task.
        '''
        self.oLoggerThread.PostLog(Logger.LOG_BOTH_PRINT, self.GetApduStr(apdu, False))
        # If we are not processing and the incoming APDU has payload, start processing
        if not self.bGBTProcessing:
            if (apdu.BD != None):
                self.oLoggerThread.PostLog(Logger.LOG_CONSOLE_PRINT, "New stream from client")
                # Let's get going
                self.StartGBT()
        self.ProcessGBTAPDU(apdu)

    def HandleEvent(self, event):
        '''
        Pure virtual method to handle the event obtained from the queue.
        '''
        if event.evtType == GBT.EVT_PEER_MSG:
            if self.msgCount in GBT.aSvrDropMsgs:
                self.DropMsgFromClient(event.data)
            else:
                self.HandleMsgFromClient(event.data)
            self.msgCount += 1
        elif event.evtType == GBT.EVT_SVR_INVOKE_ACC_RSP:
            self.InvokeAccessResponse(event.data)
        elif event.evtType == GBT.EVT_TIMER_EXPIRY_MSG:
            self.oLoggerThread.PostLog(Logger.LOG_CONSOLE_PRINT, "Server timer expired")
            self.CheckRQandFillGaps()

###############################################################################
# Function : GBTClientThreadMain
#
# Main function. Used for test if module
###############################################################################

def GBTServerThreadMain():
    pass

if __name__ == '__main__':
    GBTServerThreadMain()

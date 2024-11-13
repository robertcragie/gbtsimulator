###############################################################################
#
# MODULE:             GBT Simulator Application
#
# AUTHOR:             Robert Cragie
#
# DESCRIPTION:        Logger class
#
###############################################################################
#
#  Copyright (c) 2024 Gridmerge Ltd. All Rights Reserved.
#
###############################################################################

import EvQThread
import PrintData

EVT_LOGGER_MSG = 0

LOG_CONSOLE_PRINT = 1
LOG_LOGGER_PRINT = 2
LOG_BOTH_PRINT = 3

###############################################################################
# Class : cLogEvt
#
# Structure to hold general event
###############################################################################

class cLogEvt():
    def __init__(self, evtType, mask=1, sLog=None):
        self.evtType = evtType
        self.mask = mask
        self.sLog = sLog

###############################################################################
# Class : cLogger
#
# Structure to hold Logger
###############################################################################

class cLogger:
    def __init__(self, sFilename, bLog):
        self.oFile = None
        self.sFilename = sFilename
        self.bLog = bLog

    def __del__(self):
        if self.oFile is not None:
            self.CloseFile()

    def Log(self, bLog):
        self.bLog = bLog

    def Print(self, sData):
        if self.bLog:
            if self.oFile is not None:
                self.oFile.write(sData)
                self.oFile.write('\n')

    def PrintData(self, sData):
        if self.bLog:
            PrintData.PrintData(sData, 0, 16)
            if self.oFile is not None:
                PrintData.PrintData(sData, 0, 16, 0, 2, self.oFile)

    def OpenFile(self):
        self.oFile = open(self.sFilename, "w")

    def CloseFile(self):
        if self.oFile is not None:
            self.oFile.close()
            self.oFile = None

###############################################################################
# Class : cLoggerThread
#
# Logger Thread class
###############################################################################

class cLoggerThread(EvQThread.cEvQThread):
    '''
    Logger Thread class. Provides a thread of execution for
    handling logger events. This allows serialised printing
    and logging.
    '''

    # Constructor
    def __init__(self):
        EvQThread.cEvQThread.__init__(self)
        self.oThread.name = "Logger Thread"
        self.bUseEvent = True # Set this to True to send event to thread, False to print directly
        self.oLogger = cLogger("msc.txt", True)
        self.oLogger.OpenFile()
        self.oLogger.Print("@startuml")
        self.oLogger.Print("skin rose")
        self.oLogger.Print("title GBT example")
        self.oLogger.Print("participant CLT as \"Client\"")
        self.oLogger.Print("participant SVR as \"Server\"")

    def PostLog(self, mask, sLog):
        if self.bUseEvent:
            self.SendEvent(cLogEvt(EVT_LOGGER_MSG, mask, sLog))
        else:
            if mask & LOG_CONSOLE_PRINT:
                print(sLog)
            if mask & LOG_LOGGER_PRINT:
                self.oLogger.Print(sLog)        

    def Stop(self):
        self.oLogger.Print("@enduml")
        self.oLogger.CloseFile()
        EvQThread.cEvQThread.Stop(self)
        
    def HandleEvent(self, event: cLogEvt):
        '''
        Pure virtual method to handle the event obtained from the queue.
        '''
        if event.evtType == EVT_LOGGER_MSG:
            if event.mask & LOG_CONSOLE_PRINT:
                print(event.sLog)
            if event.mask & LOG_LOGGER_PRINT:
                self.oLogger.Print(event.sLog)
                

###############################################################################
# Function : Main
#
# Main function. Used for test if module
###############################################################################

def Main():
    pass

if __name__ == '__main__':
    Main()

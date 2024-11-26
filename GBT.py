###############################################################################
#
# MODULE:             GBT Simulator Application
#
# AUTHOR:             Robert Cragie
#
# DESCRIPTION:        GBT classes
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


import EvQThread
import Logger
import threading
import time

# GBT constants
GBT_MAX_PAYLOAD = 10 # Keep it small for simulator

# Streaming and windowing parameters
# Current set to those imposed by GBCS
GBT_CLT_BTS = 1  # Always confirmed
GBT_CLT_BTW = 63 # The number of blocks a client can receive in one window
GBT_SVR_BTS = 1  # Always confirmed
GBT_SVR_BTW = 6  # The number of blocks a server can receive in one window

# Sequence number of message to drop (0 = first, 1 = second etc.)
aCltDropMsgs = []
aSvrDropMsgs = [0]

# Timeouts in seconds for server and client wait for message
tTimeouts = (5.0, 10.0) # Server, client

# Set self and peer parameters
GBT_CLT_WSELF = GBT_CLT_BTW
GBT_SVR_WSELF = GBT_SVR_BTW
GBT_CLT_WPEER = GBT_SVR_WSELF
GBT_SVR_WPEER = GBT_CLT_WSELF

# GBT Thread general events
EVT_PEER_MSG = 0
EVT_TIMER_EXPIRY_MSG = 1

# GBT Client thread events
EVT_CLT_INVOKE_ACC_REQ = 2

# GBT Server thread events
EVT_SVR_INVOKE_ACC_RSP = 2


# Threshold to allow breakpoint on runaway. Debug only.
GBT_RUNAWAY_THRESHOLD = 40

###############################################################################
# Class : cEvt
#
# Structure to hold general event
###############################################################################

class cEvt():
    def __init__(self, evtType, data=None):
        self.evtType = evtType
        self.data = data

###############################################################################
# Class : cGBTStateVars
#
# Structure to hold GBT state variables
###############################################################################

class cGBTStateVars():
    def __init__(self, STRself=1, Wself=1):
        # Self attributes
        self.BNAself = 0
        self.STRself = STRself
        self.Wself = Wself
        # Peer attributes
        self.BNApeer = 0
        self.STRpeer = 0
        self.Wpeer = 1
        # Tracking attribute
        self.NextBN = 1

###############################################################################
# Class : cGBTBlock
#
# Structure to hold GBT block
###############################################################################

class cGBTBlock():
    def __init__(self, LB=None, BN=None, BD=None):
        self.LB = LB
        self.BN = BN
        self.BD = BD

###############################################################################
# Class : cGBTAPDU
#
# Structure to hold GBT APDU
###############################################################################

class cGBTAPDU():
    def __init__(self, block: cGBTBlock, STR=None, W=None, BNA=None):
        self.LB = block.LB
        self.BN = block.BN
        self.BD = block.BD
        self.STR = STR
        self.W = W
        self.BNA = BNA

###############################################################################
# Class : cGBTThread
#
# GBT Thread class
###############################################################################

class cGBTThread(EvQThread.cEvQThread):
    '''
    GBT Thread class. Provides a thread of execution for
    handling events relevant to the GBT operation.
    Client and Server Threads will be derived from this class.

    Note that deliberately clumsy logic is used in places
    to reflect the flowcharts in the DLMS Green Book.
    '''

    # Constructor
    def __init__(self, BTS, BTW, bIsClient):
        EvQThread.cEvQThread.__init__(self)
        self.BTS = BTS
        self.BTW = BTW
        self.bIsClient = bIsClient
        self.bGBTProcessing = False
        self.bTimerEnabled = True
        self.oTimer = None
        self.startts = time.time_ns()
        self.ClearVars()
        # GBT state vars will be cleared when peer thread is set.
        self.iSAScnt = 0
        self.iPGAcnt = 0
        self.iCRFcnt = 0

    def ClearVars(self):
        self.oGBTStateVars = cGBTStateVars(self.BTS, self.BTW) # BTS, BTW
        self.msgCount = 0 # Used to selectively deny messages to simulate loss
        self.dSQ = {} # Use dictionary keyed by BN
        self.dRQ = {} # Use dictionary keyed by BN
    
    def SetPeerThread(self, oPeerThread):
        self.oPeerThread = oPeerThread
        # 'A priori' setting of Wpeer
        self.oGBTStateVars.Wpeer = self.oPeerThread.oGBTStateVars.Wself

    def StartGBT(self):
        # Belt 'n' braces reset of variables
        self.ClearVars()
        # 'A priori' setting of Wpeer
        self.oGBTStateVars.Wpeer = self.oPeerThread.oGBTStateVars.Wself
        # Start processing
        self.bGBTProcessing = True

    def StopGBT(self):
        # Belt 'n' braces reset of variables
        self.ClearVars()
        # 'A priori' setting of Wpeer
        self.oGBTStateVars.Wpeer = self.oPeerThread.oGBTStateVars.Wself
        # Stop processing
        self.bGBTProcessing = False

    def StartTimer(self):
        '''Start a timer.'''
        if self.bTimerEnabled and self.oTimer is None:
            #print("%s starting timer, duration %f" % (self.GetNameStr(), timeout))
            self.oTimer = threading.Timer(tTimeouts[self.bIsClient], self.HandleTimerExpiry)
            self.oTimer.start()

    def StopTimer(self):
        '''Stop a timer.'''
        if self.bTimerEnabled and self.oTimer is not None:
            #print("%s stopping timer" % self.GetNameStr())
            self.oTimer.cancel()
            self.oTimer = None

    def HandleTimerExpiry(self):
        '''Handle a timer expiry.'''
        #print("%s timer expiry" % self.GetNameStr())
        self.SendEvent(cEvt(EVT_TIMER_EXPIRY_MSG))

    def GetNameStr(self):
        return ("Server", "Client")[self.bIsClient]

    def GetApduStr(self, apdu:cGBTAPDU, bDropped:bool):
        ts = time.time_ns() - self.startts
        if apdu.BN > GBT_RUNAWAY_THRESHOLD:
            print("%s runaway!!!!!" % self.GetNameStr())
        msgtype = ('>','x')[bDropped]
        sDir = ("CLT -%c SVR" % msgtype, "SVR -%c CLT" % msgtype)[self.bIsClient] 
        return "%s: %s LB=%d, STR=%d, W=%d, BN=%d, BNA=%d, BD=%s" % (sDir, ts, apdu.LB, apdu.STR, apdu.W, apdu.BN, apdu.BNA, apdu.BD) 

    def GetSimpleApduStr(self, apdu:cGBTAPDU):
        return "LB=%d, STR=%d, W=%d, BN=%d, BNA=%d, BD=%s" % (apdu.LB, apdu.STR, apdu.W, apdu.BN, apdu.BNA, apdu.BD) 

    def DiagnosticMsg(self, sMsg):
        self.oLoggerThread.PostLog(Logger.LOG_CONSOLE_PRINT, "%s: %s" % (self.GetNameStr(), sMsg))

    def SASDiagMsg(self, sMsg):
        self.DiagnosticMsg("SAS [%d] %s" % (self.iSAScnt, sMsg))

    def PGADiagMsg(self, sMsg):
        self.DiagnosticMsg("PGA [%d] %s" % (self.iPGAcnt, sMsg))

    def CRFDiagMsg(self, sMsg):
        self.DiagnosticMsg("CRF [%d] %s" % (self.iCRFcnt, sMsg))

    # DLMS-defined functions
    # All the following methods reflect functions defined in the DLMS Green Book

    def FillSQ(self, data):
        '''
        Fill blocks to Send Queue SQ.
        This is not an explicit sub-procedure but is shown
        on the flowchart in DLMS Green Book Ed. 11 V1.0 Figure 140
        '''
        start = 0
        length = len(data)
        bn = 1 # Block number starts at 1
        while length > GBT_MAX_PAYLOAD:
            self.dSQ[bn] = cGBTBlock(0, bn, data[start:start+GBT_MAX_PAYLOAD])
            start += GBT_MAX_PAYLOAD
            length -= GBT_MAX_PAYLOAD
            bn += 1
        # Check for any residual block
        if length > 0:
            # Additional last block
            self.dSQ[bn] = cGBTBlock(1, bn, data[start:start+length])
            bn += 1
        else:
            # Previous block is the last block
            self.dSQ[bn-1].LB = 1
        # Set next block number
        self.oGBTStateVars.NextBN = bn

    def SendGBTAPDUStream(self):
        '''
        Send GBT APDU stream sub-procedure.
        See DLMS Green Book Ed. 11 V1.0 section 9.4.6.13.4.
        '''
        # Drop out if not processing
        if not self.bGBTProcessing:
            return
        
        self.SASDiagMsg("Send GBT APDU Stream")

        # "First GBT APDU to send?"
        # Initialisation will have been done prior to invocation
        # TODO?

        # "BTW = 0?"
        # TODO: Assume confirmed send

        # "SQ empty?" 
        if len(self.dSQ) == 0:
            self.SASDiagMsg("Add single block to SQ")
            # Add a single block
            bn = self.oGBTStateVars.NextBN
            # Last block management is difficult - see 9.4.6.13.4.3.2
            # On the server side, it will mostly be 0. It will only be 1
            # if acknowledging the last block from the client.
            # TODO: I don't get the LB setting for an ack.
            self.dSQ[bn] = cGBTBlock(1, bn) # Empty payload
            self.oGBTStateVars.NextBN = bn + 1

        # "Take a sequence S of blocks from SQ. SQ starts with the
        # first block and contains at most Wpeer blocks"
        # Note: The blocks are not removed from SQ until acknowledged.
        WpeerBlkcount = 0 # Use counter to ensure no more than Wpeer blocks sent in a window
        bnsSQ = sorted(self.dSQ.keys()) # Should already be in order but just in case
        for bn in bnsSQ:
            # "Send each block B of S with a GBT APDU Gs such that
            # Gs.LB = B.LB, Gs.STR = STRself, Gs.W = Wself
            # Gs.BN = B.BN, Gs.BNA = BNAself, Gs.BD = B.BD" 

            # Build APDU Gs from block. 
            # Gs.LB, Gs.BN and Gs.BD set on construction from block B
            Gs = cGBTAPDU(self.dSQ[bn])

            # Set Gs.STR
            # No more streaming if:
            # This is the last remaining block in the SQ, or 
            # This is the last block in a Wpeer window, or
            # The block in the SQ is set to be the last block
            if (bn == bnsSQ[-1]) or \
               (WpeerBlkcount == (self.oGBTStateVars.Wpeer - 1)) or \
               (self.dSQ[bn].LB == 1):
                Gs.STR = 0
            else:
                Gs.STR = self.oGBTStateVars.STRself # Will be 1 in practice

            # Set Gs.W and Gs.BNA from state vars
            # Note: These MUST have been set correctly prior to invoking this method
            Gs.W = self.oGBTStateVars.Wself
            Gs.BNA = self.oGBTStateVars.BNAself

            self.SASDiagMsg("Sending APDU %s" % self.GetSimpleApduStr(Gs))

            # Send GBT APDU
            self.oPeerThread.SendEvent(cEvt(EVT_PEER_MSG, Gs))

            # Increment block count
            WpeerBlkcount += 1

            # Run a timer if we have sent the final block in a window,
            # as we will be awaiting a response. 
            if Gs.STR == 0:
                self.SASDiagMsg("End of window")
                # Awaiting a response
                self.StartTimer()
                # Stop sending blocks from the SQ.
                break

        # Increment invocation count
        self.iSAScnt += 1

    def ProcessGBTAPDU(self, Gr:cGBTAPDU):
        '''
        Process GBT APDU sub-procedure.
        See DLMS Green Book Ed. 11 V1.0 section 9.4.6.13.5.
        '''
        # Drop out if not processing
        if not self.bGBTProcessing:
            return

        self.PGADiagMsg("Process GBT APDU")

        #if not self.bIsClient and Gr.BN == 6:
        #    print("Trap1") 
        #if not self.bIsClient and Gr.BN == 12:
        #    print("Trap2") 

        # APDU received last block in window, so stop timeout timer
        if Gr.STR == 0:
            self.StopTimer()

        # "GBT PDU is ABORT"
        # Nothing to do here

        self.PGADiagMsg("Processing APDU %s" % self.GetSimpleApduStr(Gr))

        # "Gr.BN = 1 and Gr.BNA = 0?"
        # "Initialize" (see Table 96)
        if (Gr.BN == 1) and (Gr.BNA == 0):
            # Initialise BNAself, STRself and Wself
            self.PGADiagMsg("Initialising BNAself, STRself, Wself")
            self.oGBTStateVars.BNAself = 0
            self.oGBTStateVars.STRself = self.BTS
            self.oGBTStateVars.Wself = self.BTW

        # "Gr.STR = FALSE and Gr.W = 0?"
        # TODO: Assume confirmed

        # "Gr.LB = TRUE and Gr.STR = TRUE?"
        # TODO: Assume this won't happen but print if it does 
        if (Gr.LB == 1) and (Gr.STR == 1):
            print("Incoherent fields")

        # "STRpeer = Gr.STR"
        self.oGBTStateVars.STRpeer = Gr.STR

        # "Gr.BN <= BNAself?"
        if not (Gr.BN <= self.oGBTStateVars.BNAself):
            # "Block already in RQ?"
            if not (Gr.BN in self.dRQ.keys()):
                self.PGADiagMsg("Adding to RQ")
                # "Put B in RQ with B.LB = Gr.LB, B.BN = Gr.BN, B.BD = Gr.BD"
                self.dRQ[Gr.BN] = cGBTBlock(Gr.LB, Gr.BN, Gr.BD)

        # "Wpeer = Gr.W, BNApeer = Gr.BNA"
        self.oGBTStateVars.Wpeer = Gr.W # Overrides a priori default
        self.oGBTStateVars.BNApeer = Gr.BNA
        self.PGADiagMsg("Wpeer = %d, BNApeer = %d" % (Gr.W, Gr.BNA))

        # "Remove blocks up to and including BNApeer from SQ"

        # Get sorted list of block numbers in SQ
        bnsSQ = sorted(self.dSQ.keys())

        # Remove all sent items up to and including BNApeer from SQ
        prevBlk = None
        for bn in bnsSQ:
            if bn <= self.oGBTStateVars.BNApeer:
                self.PGADiagMsg("Removing block %d from SQ" % bn)
                prevBlk = self.dSQ.pop(bn)
            else:
                break # Gone through all the low blocks

        # "Number of blocks in RQ = BTW?"
        #if (len(self.dRQ) == self.BTW):
        if (False):
            # "Confirmed stream finished. Return RQ"
            # In this case it means checking the RQ
            # This check seems superfluous as Gr.STR should always be 0 on the last block in the window
            self.PGADiagMsg("Window finished len(RQ) == BTW")
            bWindowFinished = True
        else:
            # "STRpeer = TRUE?"
            if self.oGBTStateVars.STRpeer == 1:
                self.PGADiagMsg("Window not finished")
                bWindowFinished = False
                # "Ask for next GBT APDU"
                # In this case it means waiting for the next GBT APDU
            else:
                self.PGADiagMsg("Window finished len(RQ) != BTW")
                bWindowFinished = True

        # Somehow we need to determine when a sequence has actually been sent
        if (len(self.dSQ) == 0) and (prevBlk is not None) and (prevBlk.BD is not None):
            # Last block with payload has been removed from SQ
            self.PGADiagMsg("Finished sending stream")
            self.StopTimer()
            self.StopGBT()
        elif bWindowFinished:
            # "Confirmed stream finished. Return RQ"
            # In this case it means checking the RQ
            self.CheckRQandFillGaps()

        # Increment invocation count
        self.iPGAcnt += 1

    def CheckRQandFillGaps(self):
        '''
        Check RQ and fill gaps sub-procedure.
        See DLMS Green Book Ed. 11 V1.0 section 9.4.6.13.6.
        '''
        # Drop out if not processing
        if not self.bGBTProcessing:
            return

        self.CRFDiagMsg("Check RQ and Fill Gaps")
            
        # "Confirmed stream"
        # TODO: Assume confirmed

        # Get sorted list of block numbers in RQ
        bnsRQ = sorted(self.dRQ.keys()) # Should already be in order but just in case

        # "RQ empty?"
        if len(bnsRQ) == 0:
            self.CRFDiagMsg("RQ empty")
            # "Recover all blocks in the window:
            # (Do not update BNAself)
            # Wself = BTW"
            self.oGBTStateVars.Wself = self.BTW            
            self.SendGBTAPDUStream()
            self.StartTimer()
        else:
            # "Gaps?"
            # The procedure is of course somewhat more convoluted :-)
            # Anchor the initial BN check at 0. The first block is always BN = 1
            # so no initial gaps will give a gap size of 1, which is what we want
            bnCheck = 0
            gap = False
            for bn in bnsRQ:
                gapSize = bn - bnCheck
                if gapSize > 1:
                    gap = True
                    # Stop checking
                    break
                # Set the BN check to the BN just checked
                bnCheck = bn
            if gap == True:
                # Recover blocks in the first gap:
                # BNAself = B.BN before first gap
                # Wself <= GapSize of the first gap
                # TODO: Note: cannot be larger than window
                #self.oGBTStateVars.BNAself = bnCheck + 1
                self.oGBTStateVars.BNAself = bnCheck
                self.oGBTStateVars.Wself = gapSize - 1            
                self.CRFDiagMsg("Gap, BNAself %d, Wself %d" % (self.oGBTStateVars.BNAself, self.oGBTStateVars.Wself))
            else:
                self.oGBTStateVars.BNAself = bn
                self.oGBTStateVars.Wself = self.BTW            
                self.CRFDiagMsg("No gap, BNAself %d, Wself %d" % (self.oGBTStateVars.BNAself, self.oGBTStateVars.Wself))

            # Send acknowledgement
            self.SendGBTAPDUStream()

            if gap == False:
                # Stop if the receive queue has a complete stream
                # Check the block with the highest block number in the RQ
                blk = self.dRQ[bnsRQ[-1]]
                if (blk.LB == 1) and (blk.BD != None):
                    # Invoke indication/confirm?
                    # Stop processing
                    self.CRFDiagMsg("Finished receiving stream")
                    self.StopTimer()
                    self.StopGBT()
                else:
                    self.CRFDiagMsg("Continue (1)")
                    self.StartTimer()
            else:
                self.CRFDiagMsg("Continue (2)")
                self.StartTimer()

        # Increment invocation count
        self.iCRFcnt += 1

###############################################################################
# Function : GBTMain
#
# Main function. Used for test if module
###############################################################################

def GBTMain():
    pass

if __name__ == '__main__':
    GBTMain()

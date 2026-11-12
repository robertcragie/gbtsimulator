###############################################################################
#
# MODULE:             GBT Simulator Application CLI
#
# AUTHOR:             Robert Cragie
#
# DESCRIPTION:        Simple CLI application to show GBT simulation
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

import signal
import sys
import time
import pickle
import GBT
import GBTClientThread
import GBTServerThread
import Logger

###############################################################################
# Class : cGBTSimulatorCLI
#
# GBT simulator CLI class.
###############################################################################

class cGBTSimulatorCLI():
    '''
    GBTSimulator CLI version.
    '''

    ###############################################################################
    # Method : __init__
    #
    # Constructor
    ###############################################################################

    def __init__(self):
        # GBT client and server threads
        self.oGBTClientThread = GBTClientThread.cGBTClientThread()
        self.oGBTServerThread = GBTServerThread.cGBTServerThread()

        # Logger thread
        self.oLoggerThread = Logger.cLoggerThread(False)

        # Exchange peer handles
        self.oGBTClientThread.SetPeerThread(self.oGBTServerThread)
        self.oGBTServerThread.SetPeerThread(self.oGBTClientThread)

        # Set logger thread in each GBT thread
        self.oGBTClientThread.oLoggerThread = self.oLoggerThread
        self.oGBTServerThread.oLoggerThread = self.oLoggerThread

        # Start threads
        self.oGBTClientThread.Start()
        self.oGBTServerThread.Start()
        self.oLoggerThread.Start()
        
        try:
            oCfgFile = open('gbtsim.cfg','rb')
            oUnpickler = pickle.Unpickler(oCfgFile)
            self.sPayload = oUnpickler.load()
            oCfgFile.close()
        except:
            print('Config file error, using defaults')
            self.sPayload = 'jsdhshdhasufiurugfirivcberufrieugf'

    ###############################################################################
    # Method : Shutdown
    #
    # Save data and stop threads
    ###############################################################################

    def Shutdown(self):
        '''Save data and stop threads'''
        oCfgFile = open('gbtsim.cfg','wb')
        oPickler = pickle.Pickler(oCfgFile)
        oPickler.dump(self.sPayload)
        oCfgFile.close()
        self.oGBTClientThread.Stop()
        self.oGBTServerThread.Stop()
        self.oLoggerThread.Stop()
 
    ###############################################################################
    # Method : ClientInvoke
    #
    # Invoke Access-request
    ###############################################################################

    def ClientInvoke(self):
        self.oGBTClientThread.SendEvent(GBT.cEvt(GBT.EVT_CLT_INVOKE_ACC_REQ, self.sPayload))

    ###############################################################################
    # Method : ServerInvoke
    #
    # Invoke Access-response
    ###############################################################################

    def ServerInvoke(self):
        self.oGBTServerThread.SendEvent(GBT.cEvt(GBT.EVT_SVR_INVOKE_ACC_RSP, self.sPayload))

if __name__ == '__main__':
    try:
        oCLIApp = cGBTSimulatorCLI()
        #signal.signal(signal.SIGINT, sigint_handler)
        oCLIApp.ClientInvoke()
        # Wait for 10 minutes.
        # This is naff but prevents the main thread exiting early,
        # leaving the other threads in limbo.
        time.sleep(600)
        print("Shutting down after 10 minutes")
        oCLIApp.Shutdown()
    except KeyboardInterrupt:
        print("Shutting down on ctrl-c")
        # Can't shutdown too early.
        # What's missing is ensuring the client and server threads have finished
        # This problem doesn't exist with the wxApp as closing the app shuts down.
        oCLIApp.Shutdown()


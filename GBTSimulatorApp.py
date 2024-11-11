###############################################################################
#
# MODULE:             GBT Simulator Application
#
# AUTHOR:             Robert Cragie
#
# DESCRIPTION:        Simple application to show GBT simulation
#
###############################################################################
#
#  Copyright (c) 2024 Gridmerge Ltd. All Rights Reserved.
#
###############################################################################

import pickle
import wx
import About
import GBT
import GBTClientThread
import GBTServerThread
import Logger

###############################################################################
# Class : cGBTSimulatorFrame
#
# Main frame in app.
###############################################################################

class cGBTSimulatorFrame(wx.Frame):
    '''
    GBTSimulatorFrame.  It just shows a few controls on a wxPanel,
    and has a simple menu.
    '''

    ###############################################################################
    # Method : __init__
    #
    # Constructor
    ###############################################################################

    def __init__(self, parent, sTitle, sVersion):
        self.sTitle = sTitle
        self.sVersion = sVersion
        wx.Frame.__init__(self, parent, -1, self.sTitle + " " + self.sVersion,
                          pos=(150, 150), size=(400, 400),  style=wx.DEFAULT_FRAME_STYLE)

        ########
        # Data #
        ########

        # GBT client and server threads
        self.oGBTClientThread = GBTClientThread.cGBTClientThread()
        self.oGBTServerThread = GBTServerThread.cGBTServerThread()

        # Logger thread
        self.oLoggerThread = Logger.cLoggerThread()

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
            self.sPayload = ''
 
        self.Bind(wx.EVT_CLOSE, self.EvtClose)

        ############
        # Menu bar #
        ############

        # Create the menubar
        oMenuBar = wx.MenuBar()

        # and a menu
        oMenuFile = wx.Menu()

        # Add an item to the menu, using \tKeyName automatically
        # creates an accelerator, the third param is some help text
        # that will show up in the statusbar
        oMenuFile.Append(wx.ID_ABOUT, "&About...\tAlt-A", "About")
        oMenuFile.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit GBT Simulator Application")

        # Bind the menu events to event handlers
        self.Bind(wx.EVT_MENU, self.MenuFileAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.MenuFileClose, id=wx.ID_EXIT)

        # and put the menu on the menubar
        oMenuBar.Append(oMenuFile, "&File")
        self.SetMenuBar(oMenuBar)

        ##############
        # Status bar #
        ##############

        self.CreateStatusBar()

        #########
        # Panel #
        #########

        # Now create the Panel to put the other controls on.
        oPanel = wx.Panel(self)

        #### Client invoke

        # Add Client invoke button
        self.oGBTClientInvokeButton = wx.Button(oPanel, -1, "Client", size = (60,30))
        # Bind the handler to the button
        self.Bind(wx.EVT_BUTTON, self.OnGBTClientInvokeButton, self.oGBTClientInvokeButton)

        #### Server invoke

        # Add Server invoke button
        self.oGBTServerInvokeButton = wx.Button(oPanel, -1, "Server", size = (60,30))
        # Bind the handler to the button
        self.Bind(wx.EVT_BUTTON, self.OnGBTServerInvokeButton, self.oGBTServerInvokeButton)

        #### Payload window

        # Set up a payload window
        self.oPayloadTextCtrl = wx.TextCtrl(oPanel, -1, self.sPayload, size = (400,200), style = wx.TE_MULTILINE)
        self.Bind(wx.EVT_TEXT, self.EvHPayloadText, self.oPayloadTextCtrl)

        # Use a sizer to layout the controls, stacked vertically and with
        # a 10 pixel border around each
        oVSizer = wx.BoxSizer(wx.VERTICAL)

        # Invoke
        oStaticBox = wx.StaticBox(oPanel, -1, "Invoke")
        oBox = wx.StaticBoxSizer(oStaticBox, wx.HORIZONTAL)
        oBox.Add(self.oGBTClientInvokeButton, 0, wx.ALL, 5)
        oBox.Add(self.oGBTServerInvokeButton, 0, wx.ALL, 5)
        # ...add more controls to the horizontal sizer
        oVSizer.Add(oBox, 0, wx.ALL, 5)

        # Payload window
        oStaticBox = wx.StaticBox(oPanel, -1, "Payload")
        oBox = wx.StaticBoxSizer(oStaticBox, wx.HORIZONTAL)
        oBox.Add(self.oPayloadTextCtrl, 0, wx.ALL, 5)
        # ...add more controls to the horizontal sizer
        oVSizer.Add(oBox, 0, wx.ALL, 5)

        # ...create more HSizers and controls and add to VSizer

        oPanel.SetSizer(oVSizer)
        oPanel.SetAutoLayout(True)
        oPanel.Layout()

    ###############################################################################
    # Method : SaveData
    #
    # Saves data in pickle format
    ###############################################################################

    def SaveData(self):
        '''Saves data in a config file.'''
        oCfgFile = open('gbtsim.cfg','wb')
        oPickler = pickle.Pickler(oCfgFile)
        oPickler.dump(self.sPayload)
        oCfgFile.close()

    ###############################################################################
    # Method : EvtClose
    #
    # Event handler for global close
    ###############################################################################

    def EvtClose(self, evt):
        '''Event handler for global close.'''
        self.SaveData()
        self.oGBTClientThread.Stop()
        self.oGBTServerThread.Stop()
        self.oLoggerThread.Stop()
        self.Destroy()

    ###############################################################################
    # Method : MenuFileAbout
    #
    # Event handler for menu about
    ###############################################################################

    def MenuFileAbout(self, evt):
        oDlg = About.MyAboutBox(None, self.sTitle, self.sTitle + "<br>" + self.sVersion)
        oDlg.ShowModal()
        oDlg.Destroy()

    ###############################################################################
    # Method : MenuFileClose
    #
    # Event handler for menu close
    ###############################################################################

    def MenuFileClose(self, evt):
        '''Event handler for menu close.'''
        # print("Closed by MenuClose")
        self.Close()

    ###############################################################################
    # Method : OnGBTClientInvokeButton
    #
    # Invoke Access-request
    ###############################################################################

    def OnGBTClientInvokeButton(self, evt):
        self.oGBTClientThread.SendEvent(GBT.cEvt(GBT.EVT_CLT_INVOKE_ACC_REQ, self.sPayload))

    ###############################################################################
    # Method : OnGBTServerInvokeButton
    #
    # Invoke Access-response
    ###############################################################################

    def OnGBTServerInvokeButton(self, evt):
        self.oGBTServerThread.SendEvent(GBT.cEvt(GBT.EVT_SVR_INVOKE_ACC_RSP, self.sPayload))

    ###############################################################################
    # Method : EvHPayloadText
    #
    # Payload text box character handler
    ###############################################################################

    def EvHPayloadText(self, event):
        self.sPayload = self.oPayloadTextCtrl.GetValue()
        #print(self.sPayload)

###############################################################################
# Class : GBTSimulatorApp
#
# GBT simulator application class subclassed from wx.App
###############################################################################

class cGBTSimulatorApp(wx.App):
    def OnInit(self):
        oFrame = cGBTSimulatorFrame(None, "GBT Simulator Application", "v1.0")
        oFrame.Show(True)
        self.SetTopWindow(oFrame)
        return True

###############################################################################
# Function : GBTSimulatorAppMain
#
# Main function. Used for test if module
###############################################################################

def GBTSimulatorAppMain():
    oApp = cGBTSimulatorApp(False)
    oApp.MainLoop()

if __name__ == '__main__':
    GBTSimulatorAppMain()

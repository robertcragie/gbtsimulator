###############################################################################
#
# MODULE:             GBT Simulator Application
#
# AUTHOR:             Robert Cragie
#
# DESCRIPTION:        'About' dialog
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

import wx
import wx.html
import wx.lib.wxpTag

#---------------------------------------------------------------------------

class MyAboutBox(wx.Dialog):
    text = '''
<html>
<body bgcolor="#c0c0c0">
<center><table bgcolor="#FFFFFF" width="100%%" cellspacing="0"
cellpadding="0" border="0">
<tr>
    <td align="center">
    <p><img src="gridmerge.gif"></p>
    </td>
</tr>
<tr>
    <td align="center">
    <h1>%s</h1>
    </td>
</tr>
</table>

<p>Copyright (c) 2024 Gridmerge Ltd.</p>
<p>This software is based on <a href="https://www.python.org/">Python 3</a> and <a href="https://www.wxpython.org/">wxPython</a></p>
<p><wxp module="wx" class="Button">
    <param name="label" value="Close">
    <param name="id"    value="ID_OK">
</wxp></p>
</center>
</body>
</html>
'''
    def __init__(self, parent, sTitleText, sInitText):
        wx.Dialog.__init__(self, parent, -1, 'About %s' % sTitleText,)
        html = wx.html.HtmlWindow(self, -1, size=(320, -1))
        if "gtk2" in wx.PlatformInfo:
            html.NormalizeFontSizes()
        html.SetPage(self.text % sInitText)
        ir = html.GetInternalRepresentation()
        html.SetSize( (ir.GetWidth()+25, ir.GetHeight()+25) )
        self.SetClientSize(html.GetSize())
        self.CentreOnParent(wx.BOTH)

#---------------------------------------------------------------------------

if __name__ == '__main__':
    app = wx.PySimpleApp()
    dlg = MyAboutBox(None)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()


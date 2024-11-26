###############################################################################
#
# MODULE:             Briareus Gateway Application
#
# AUTHOR:             Robert Cragie
#
# DESCRIPTION:        Function to print(data in a formatted way)
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

import struct

def PrintData(sData, iBase, iNumPerLine, iFormat=0, iMode=0, oDest=None):
    iOffset = 0
    iBufSize = len(sData)
    sPrint = ""
    while iBufSize > 0:
        if iBufSize < iNumPerLine:
            iNumPerLine = iBufSize;
            sPrint += DisplayDataLine(sData[iOffset:], iBase, iOffset, iNumPerLine, iFormat, iMode, oDest)
            iBufSize = 0
        else:
            sPrint += DisplayDataLine(sData[iOffset:iOffset + iNumPerLine], iBase, iOffset, iNumPerLine, iFormat, iMode, oDest)
            sPrint += '\n'
            iOffset = iOffset + iNumPerLine
            iBufSize = iBufSize - iNumPerLine
    return sPrint

def DisplayDataLine(sData, iBase, iOffset, iNumPerLine, iFormat, iMode, oDest):
    # This is a rather terse, very 'pythony' line of code. C programmers might struggle...
    # '%02X ' * mult => a string of '%02X's, e.g. '%02X ' * 3 => '%02X %02X %02X '
    # The '%' operator with strings is the replacement operator.
    # So: '%d' % 1 => '1'.  The C equivalent is printf("%d",1);
    # or '%d%d%d' % (1,2,3) => '123'. The C equivalent is printf("%d%d%d",1, 2, 3);
    # Note in the last example, a tuple is used as the argument to obtain the three values.
    # So, if mult = 16, '%db' % mult => '16b'
    # struct.unpack() returns a tuple which is used as the argument for all the '%02X 's
    # produced by '%02X ' * mult. The number of elements in the tuple must match the number
    # of matches in the string
    if iFormat == 1:
        # Halfword
        iNumPerLine = iNumPerLine >> 1
        sAddrFmt = '%08X: '
        sDataFmt = '%04X '
        sUnpack = '=%dH' % iNumPerLine
    elif iFormat == 2:
        # Word
        iNumPerLine = iNumPerLine >> 2
        sAddrFmt = '%08X: '
        sDataFmt = '%08X '
        sUnpack = '=%dL' % iNumPerLine
    elif iFormat == 3:
        # 'od -v -Ax -t x4' format
        iNumPerLine = iNumPerLine >> 2
        sAddrFmt = '%06x '
        sDataFmt = '%08x '
        sUnpack = '>%dL' % iNumPerLine
    else:
        # Byte by default
        sAddrFmt = '%08X: '
        sDataFmt = '%02X '
        sUnpack = '%dB' % iNumPerLine

    sLine = sAddrFmt % (iBase + iOffset) + sDataFmt * iNumPerLine % struct.unpack(sUnpack, sData)
    if iMode == 0:
        # print(to console)
        print(sLine)
    elif iMode == 1:
        # Text control mode - oDest is a Text Control object
        oDest.AppendText(sLine + '\n')
    elif iMode == 2:
        # File mode - oDest is a file object
        oDest.write(sLine[:-1] + '\n')
    elif iMode == 3:
        # Simple hex dump
        sLine = sDataFmt * iNumPerLine % struct.unpack(sUnpack, sData)
    return sLine

###############################################################################
# Function : PrintDataMain
#
# Main function. Used for test if module
###############################################################################

def PrintDataMain():
    sData = struct.pack('16b', 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15)
    PrintData(sData, 0x100, 8, 0, 0)
    PrintData(sData, 0x200, 8, 1, 0)
    PrintData(sData, 0x300, 8, 2, 0)
    PrintData(sData, 0x400, 8, 3, 0)

if __name__ == '__main__':
    PrintDataMain()

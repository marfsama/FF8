#!/usr/bin/env python3

from tools import *
from tim import *

from functools import partial
import os
import sys


basePath = "/home/marf/project/ff8/x/main_chr/"
#fileName = "d026.mch"

HEADER_SIZE = 0x100



def readHeader(file):
    """ header lesen """
    offsets = []
    for i in range(8):
        offsets.append(readu32(file))

    """ die ZAhl im oberen word des offsets könnte die Textur-Nummer sein.
    """

    print("==== File Header ====")
    for offset in offsets:
        printHex("offset", offset)

    return offsets

def findModelOffset(offsets):
    found = False
    for offset in offsets:
        if found:
            return offset
        if offset == 0xffffffff:
            found = True
    return -1

def main():
    fileName = sys.argv[1]
    print(fileName)
    length = os.stat(basePath + fileName).st_size
    print("file length:", length)
    with open(basePath + fileName, "rb") as mchFile:
        offsets = readHeader(mchFile)


        print("==== Other Daten ====")
        """ eintrag direkt nach dem header lesen """
        modelOffset = findModelOffset(offsets)
        mchFile.seek(modelOffset)
        printHex("tell", mchFile.tell())

        numEntries1 = readu32(mchFile)
        numEntries2 = readu32(mchFile)
        numEntries3 = readu32(mchFile)
        numEntries4 = readu32(mchFile)
        printHex("numEntries1", numEntries1)
        printHex("numEntries2", numEntries2)
        printHex("numEntries3", numEntries3)
        printHex("numEntries4", numEntries4)
        # skip unknown stuff
        stuff = []
        for s in range(3):
            value = readu32(mchFile)
            stuff.append(value)
            printHex(str(s+1), value)

        temp1 = readu16(mchFile)
        temp2 = readu16(mchFile)
        printHex("temp1", temp1)
        printHex("temp2", temp2)

        # always 64, as the size of the header is 64 bytes
        listoffset1 = readu32(mchFile)
        listoffset2 = readu32(mchFile)
        listoffset3 = readu32(mchFile)
        listoffset4 = readu32(mchFile)
        printHex("9 listoffset1", listoffset1)
        printHex("10 listoffset2", listoffset2)
        printHex("11 listoffset3", listoffset3)
        printHex("11 listoffset4", listoffset4)
        otherOffsets = []
        for s in range(4):
            value = readu32(mchFile)
            stuff.append(value)
            printHex(str(s+1), value)

        print("entries1 - size: 64 bytes -", numEntries1, "entries - face data?")
        """ 
            Der untere Teil des Value1 geht bis 0x18 (24). Das entspricht der 0-basierten
            Indizierung dieses Arrays. Könnte das ein "Next" Pointer oder so sein?
            Oder wird damit ein Triangle Strip gebildet und eine negative Zahl gibt das 
            Ende an? Eher unwahrscheinlich, da die indizes nicht alle Vertices abgraben
        """
        printHex("tell", mchFile.tell())
        printHex("tell", mchFile.tell() - modelOffset)
        for i in range(numEntries1):
            value1 = readu32(mchFile)
            empty = readu32(mchFile)
            value2 = readu32(mchFile)
            skip = []
            for j in range(13):
                skip.append(readu32(mchFile))
            #print("{0}: 0x{1:x}, 0x{2:x}, 0x{3:x}, {4}".format(i+1, value1, empty, value2, skip))

        print("entries2 - size: 8 bytes -", numEntries2, " entries - vertices? x,y,z,w?")
        printHex("tell", mchFile.tell())
        printHex("tell", mchFile.tell() - modelOffset)

        for i in range(numEntries2):
            values = read16(mchFile), read16(mchFile), read16(mchFile), read16(mchFile)
            # print("{0}: {1}".format(i+1, values))

        print("entries3 - size: 1 byte -",numEntries3,"entries - irgendein bitmask zeugs?")
        printHex("tell", mchFile.tell())
        printHex("tell", mchFile.tell() - modelOffset)

        entries3 = []
        for i in range(numEntries3):
            entries3.append(readu8(mchFile))
        #print("0: {0}".format(entries3))

        print("entries4 - size: 64 bytes -", numEntries4,"entries - polygon and normals data?")
        printHex("tell", mchFile.tell())
        printHex("tell", mchFile.tell() - modelOffset)
        for i in range(numEntries4):
            value1 = readu16(mchFile)
            value2 = readu16(mchFile)
            value3 = readu32(mchFile)
            value4 = readu32(mchFile)
            # index into vertex array            
            value5 = readu16(mchFile)
            value6 = readu16(mchFile)
            value7 = readu16(mchFile)
            value8 = readu16(mchFile)
            value9 = readu16(mchFile)
            value10 = readu16(mchFile)
            value11 = readu16(mchFile)
            value12 = readu16(mchFile)
            skip = []
            for j in range(9):
                skip.append("0x{0:x}".format(readu32(mchFile)))
            # print("{0}: 0x{1:x} 0x{2:x} 0x{3:x} 0x{4:x}".format(i+1, value1, value2, value3, value4))
            #print("{0}: 0x{1:x} 0x{2:x} 0x{3:x} 0x{4:x} 0x{6:x} 0x{6:x} 0x{7:x} 0x{8:x}".format(i+1, value5, value6, value7, value8, value9, value10, value11, value12))
            print("{0}: {1}".format(i+1, skip)) 

        print("entries5 - size: ? bytes -", 1,"entries")
        printHex("tell", mchFile.tell())
        printHex("tell", mchFile.tell() - modelOffset)
main()


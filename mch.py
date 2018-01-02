#!/usr/bin/env python3

from tools import *
from tim import *
from mch_model import *

from functools import partial
import os
import sys


basePath = "/home/marf/project/ff8/x/main_chr/"


def readHeader(file):
    """ header lesen """
    offsets = []
    for i in range(8):
        offsets.append(readu32(file))

    """ die ZAhl im oberen word des offsets könnte die Textur-Nummer oder texture unit sein.
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
    with open(basePath + fileName, "rb") as mchFile:
        offsets = readHeader(mchFile)


        print("==== Model Daten ====")
        modelOffset = findModelOffset(offsets)
        mchFile.seek(modelOffset)
        printHex("tell", mchFile.tell())

        readModel(mchFile)

        print("end of file")
        printHex("tell", mchFile.tell())
        printHex("remaining", length - mchFile.tell())




main()


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

    print("==== File Header ====")
    for offset in offsets:
        printHex("offset", offset)




def main():
    fileName = sys.argv[1]
    print(fileName)
    length = os.stat(basePath + fileName).st_size
    print("file length:", length)
    with open(basePath + fileName, "rb") as mchFile:
        readHeader(mchFile)
        """ eintrag direkt nach dem header lesen """
        mchFile.seek(HEADER_SIZE)

        image = readImage(mchFile)

        image.save("img1.jpg")

main()


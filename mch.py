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

def outputVertices(objFile, model):
    for vertex in model.vertices:
        objFile.write("v {0} {1} {2}\n".format(vertex.x, vertex.y, vertex.z))
    objFile.write("\n")

def outputFaces(objFile, model):
    faceSpan = model.faceSpans[0]
    objFile.write("f {0} {1} {2}\n".format(faceSpan.startIndex+1, faceSpan.startIndex+2, faceSpan.startIndex+3))
     


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

        model = readModel(mchFile)
        print(str(model))
        print(str(model.vertices[0]))

        for span in model.faceSpans:
            print(str(span))

        print("end of file")
        printHex("tell", mchFile.tell())
        printHex("remaining", length - mchFile.tell())

        with open("out.obj", "w") as out:
            out.write("g default\n\n")
            outputVertices(out, model)
            outputFaces(out, model)


main()


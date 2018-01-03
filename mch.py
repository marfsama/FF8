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


def outputVertex(objFile, vertex, faceIndex):
        objFile.write("v {0} {1} {2}\n".format(vertex.x, vertex.y, vertex.z))
        objFile.write("v {0} {1} {2}\n".format(vertex.x+1, vertex.y, vertex.z))
        objFile.write("v {0} {1} {2}\n".format(vertex.x, vertex.y+1, vertex.z))
        objFile.write("f {0} {1} {2}\n".format(faceIndex, faceIndex+1, faceIndex+2))

def outputVertexCloud(objFile, model):
    faceIndex = 1
    for vertex in model.vertices:
        outputVertex(objFile, vertex, faceIndex)
        faceIndex += 3

def outputFaceSpan(objFile, model, faceSpan):
    faceIndex = 1
    for vertexIndex in range(faceSpan.length):
        vertex = model.vertices[ faceSpan.startIndex+vertexIndex ]
        outputVertex(objFile, vertex, faceIndex)
        faceIndex += 3

#    objFile.write("l ")
#    for vertexIndex in range(faceSpan.length):
#        objFile.write("\n")
#    objFile.write("\n")



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
            outputFaceSpan(out, model, model.faceSpans[0])


main()


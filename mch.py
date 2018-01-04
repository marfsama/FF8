#!/usr/bin/env python3

from tools import *
from tim import *
from mch_model import *

from functools import partial
import os
import sys


basePath = "main_chr/"


def readHeader(file):
    """ header lesen """
    offsets = []
    for i in range(8):
        offsets.append(readu32(file))

    """ die ZAhl im oberen word des offsets könnte die Textur-Nummer oder texture unit sein.
    """

#    print("==== File Header ====")
#    for offset in offsets:
#        printHex("offset", offset)

    return offsets

def findModelOffset(offsets):
    found = False
    for offset in offsets:
        if found:
            return offset
        if offset == 0xffffffff:
            found = True
    return -1


def statisticsList1(model):
    minValue = 1000
    maxValue = -1000
    for index, face in enumerate(model.faces):
        print(index, ":", str(face))
        minValue = min(minValue, face.value3)
        maxValue = max(maxValue, face.value3)

    print("value3: ", minValue, maxValue)

def statisticsVertexList(model):
    minX, maxX = 1000, -1000
    minY, maxY = 1000, -1000
    minZ, maxZ = 1000, -1000

    for index, vertex in enumerate(model.vertices):
        print(index, ":", str(vertex))
        minX = min(minX, vertex.x)
        minY = min(minY, vertex.y)
        minZ = min(minZ, vertex.z)
        maxX = max(maxX, vertex.x)
        maxY = max(maxY, vertex.y)
        maxZ = max(maxZ, vertex.z)
    print("x: ", minX, maxX)
    print("y: ", minY, maxY)
    print("z: ", minZ, maxZ)

def statisticsList3(model):
    minValue, maxValue, sumValue = 1000, -1000, 0
    for index, entry in enumerate(model.entries3):
        print("{0:3}: dec: {1:3} hex: {1:3x} bin: {1:8b}".format(index, entry))
        minValue = min(minValue, entry)
        maxValue = max(maxValue, entry)
        sumValue += entry
    print("    value min:",minValue," max:", maxValue,"sum:",sumValue)


def main():
    fileName = sys.argv[1]
    print(fileName)
    length = os.stat(basePath + fileName).st_size
    with open(basePath + fileName, "rb") as mchFile:
        offsets = readHeader(mchFile)


        print("==== Model Daten ====")
        modelOffset = findModelOffset(offsets)
        mchFile.seek(modelOffset)

        model = readModel(mchFile)

        print("end of file")
        printHex("tell", mchFile.tell())
        printHex("remaining", length - mchFile.tell())


        for index, entry in enumerate(model.entries4):
            pass

main()


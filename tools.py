#!/usr/bin/env python3
import struct

def readlist(function, file, count):
    list = []
    for i in range(count):
        list.append(function(file))
    return list

def readu32(file):
    data = file.read(4);
    return struct.unpack("I", data)[0]

def readfloat(file):
    data = file.read(4);
    return struct.unpack("f", data)[0]

def readu16(file):
    data = file.read(2);
    return struct.unpack("H", data)[0]

def read16(file):
    data = file.read(2);
    return struct.unpack("h", data)[0]

def readu8(file):
    data = file.read(1);
    return struct.unpack("B", data)[0]

def printHex(name, number):
    print(name, ":" , number, "0x{0:x}".format(number))

def printHexListOneLine(name, offset):
    pass

def printHexListMultiLine(name, offsetList):
    for index in range(len(offsetList)):
        printHex(name+str(index+1), offsetList[index])


def fromPsColor(color, useAlpha = True):
    r = int((color & 31) << 3)
    g = int((color >> 5 & 31) << 3)
    b = int((color >> 10 & 31) << 3)
    a = (int(color >> 15 & 1) * 255 if useAlpha else 0)
    return (r,g,b,a)


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

def read32(file):
    data = file.read(4);
    return struct.unpack("i", data)[0]

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

def read8(file):
    data = file.read(1);
    return struct.unpack("b", data)[0]

def printHex(name, number):
    print(name, ":" , number, "0x{0:x}".format(number))

def printHexListOneLine(name, numbers):
    s = "";
    for number in numbers:
        s += "{0} 0x{1:x}, ".format(number, number)
    print(name, ":", s)

def printHexListMultiLine(name, numbers):
    for index in range(len(numbers)):
        printHex(name+str(index+1), numbers[index])

def toHex(list):
    return ["0x{0:x}".format(s) for s in list] 

def fromPsColor(color, useAlpha = True):
    r = int((color & 31) << 3)
    g = int((color >> 5 & 31) << 3)
    b = int((color >> 10 & 31) << 3)
    a = (int(color >> 15 & 1) * 255 if useAlpha else 0)
    return (r,g,b,a)

class MinMax:
    def __init__(self):
        self.init = True
        self.min = 0;
        self.max = 0;

    def add(self, value):
        if self.init:
            self.init = False
            self.min = value
            self.max = value
        else:
            self.min = min(self.min, value)
            self.max = max(self.max, value)

    def addAll(self, values):
        for value in values:
            self.add(value)

    def __repr__(self):
        return "min: {0} max: {1}".format(self.min, self.max)


class Offsets:
    def __init__(self, offsetNames):
        self.offsetNames = offsetNames
        self.offsets = {}
        self.sizes = {}


    def setOffsets(self, offsets, totalSize = 0):
        lastName = None
        lastOffset = 0        
        for index, offsetName in enumerate(self.offsetNames):
            self.offsets[offsetName] = offsets[index]

    def getOffset(self, offsetName):    
        return self.offsets[offsetName]

    def __str__(self):
        lines = ["{0}: 0x{1:x}".format(offsetName, self.offsets[offsetName])  for offsetName in self.offsetNames]
        return "\n".join(lines)



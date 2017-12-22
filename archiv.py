#!/usr/bin/env python3
import struct
from functools import partial

basePath = "/home/marf/project/ff8/disk1/"
fieldIndex = "FI"
fieldNames = "FL"

class Entry:
    def __init__(self, length, offset, checksum, path):
        self.length = length
        self.offset = offset
        self.checksum = checksum
        self.path = path

    def __str__(self):
        return "{name}: {{length: {length}, offset: {offset}, checksum: {checksum}, path: {path} }}".format(name=type(self).__name__, **vars(self))


def fullPath(fileName, type):
    return basePath+fileName+"."+type

def decodeOffsets(fileName):
    with open(fullPath(fileName, fieldIndex), "rb") as fieldIndexFile:
        for data in iter(partial(fieldIndexFile.read, 12), b''):
            unpacked = struct.unpack("iii", data)
            yield unpacked

def decodeFilesNames(fileName):
    with open(fullPath(fileName, fieldNames), "r") as fieldNamesFile:
        for line in iter(partial(fieldNamesFile.readline), ''):
            yield line.strip()

def main():
    fileName = "FIELD"
    entries = []
    for item in zip(decodeOffsets(fileName), decodeFilesNames(fileName)):
        entries.append(Entry(*item[0], item[1]))
        
    [ print(x) for x in entries ]


main()


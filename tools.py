#!/usr/bin/env python3
import struct

def readu32(file):
    data = file.read(4);
    return struct.unpack("i", data)[0]

def readu16(file):
    data = file.read(2);
    return struct.unpack("h", data)[0]

def printHex(name, offset):
    print(name, ":" , offset, "0x{0:x}".format(offset))


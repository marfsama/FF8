#!/usr/bin/env python3

from tools import *
from functools import partial
import os
import sys

from PIL import Image, ImageDraw

basePath = "/home/marf/project/ff8/x/main_chr/"
#fileName = "d026.mch"

HEADER_SIZE = 0x100

class BitPerPixel:
    def __init__(self, id, bpp, colorPaletSize):
        self.id = id
        self.bpp = bpp
        self.colorPaletSize = colorPaletSize

    def __str__(self):
        return "{name}: {{id: {id}, bpp: {bpp}, colorPaletSize: {colorPaletSize}}}".format(name=type(self).__name__, **vars(self))

def bitsPerPixel(id):
    return {
        0: BitPerPixel(0, 4, 16),
        1: BitPerPixel(1, 8, 256),
        2: BitPerPixel(2, 16, 0),
        3: BitPerPixel(3, 24, 0)
    }.get(id)


def readHeader(file):
    """ header lesen """
    offsets = []
    for i in range(8):
        offsets.append(readu32(file))

    print("==== File Header ====")
    for offset in offsets:
        printHex("offset", offset)


def fromPsColor(color, useAlpha = True):
    r = int((color & 31) << 3)
    g = int((color >> 5 & 31) << 3)
    b = int((color >> 10 & 31) << 3)
    a = (int(color >> 15 & 1) * 255 if useAlpha else 0)

    return (r,g,b,a)


def main():
    fileName = sys.argv[1]
    print(fileName)
    length = os.stat(basePath + fileName).st_size
    print("file length:", length)
    with open(basePath + fileName, "rb") as mchFile:
        readHeader(mchFile)
        """ eintrag direkt nach dem header lesen """
        mchFile.seek(HEADER_SIZE)

        print("==== TIM Header ====")
        printHex("marker", readu32(mchFile))
        flags = readu32(mchFile)
        """ Note: eventuell geben die Flags auch an, ob eine Palette und ein Bild folgt.
            Also: Bits 0-2 - BPP und damit, ob eine Palette folgt
                  Bits 3 - Folgt ein Bild.
            Warum? Sowohl die Palette als auch das Bild ist in Chunks abgebildet, jeweils
                   mit Size-Header vorne dran, um den ganzen Chunk einzulesen und/oder zu
                   überspringen. Die Flags sind aber nicht Bestandteil eines Chunks. 
        """
        bpp = bitsPerPixel(flags & 3)
        hasPal = (flags >> 3) & 1
        palSize = readu32(mchFile)
        palX = readu16(mchFile)
        palY = readu16(mchFile)
        palW = readu16(mchFile)
        palH = readu16(mchFile)

        print("flags:", flags, "{0:b}b".format(flags), "bpp:", bpp, "hasPal:", hasPal)
        printHex("palSize:", palSize)
        printHex("palX:", palX)
        printHex("palY:", palY)
        printHex("palW:", palW)
        printHex("palH:", palH)

        palette = []
        for i in range(bpp.colorPaletSize):
            r,g,b,a = fromPsColor(readu16(mchFile))
            palette.append(r)
            palette.append(g)
            palette.append(b)

        width, height = 256, 256

        image = Image.new("P", (width, height), 0)
        image.putpalette(palette)
        d = ImageDraw.ImageDraw(image)
        for x in range(width):
            for y in range(height):
                color = int(x / 16) * 16 + int(y / 16)
                d.point((x,y), fill=color)

        image.convert("RGB").save("palette.jpg")

        printHex("tell:", mchFile.tell())

        imgSize = readu32(mchFile)
        imgX = readu16(mchFile)
        imgY = readu16(mchFile)
        imgW = readu16(mchFile)
        imgH = readu16(mchFile)
        printHex("imgSize:", imgSize)
        printHex("imgX:", imgX)
        printHex("imgY:", imgY)
        printHex("imgW:", imgW)
        printHex("imgH:", imgH)

        if (bpp.id == 0):
            imgW *= 4
        if (bpp.id == 1):
            imgW *= 2;

        image = Image.new("P", (imgW, imgH), 0)
        image.putpalette(palette)
        d = ImageDraw.ImageDraw(image)
        for y in range(imgH):
            for x in range(imgW):
                color = mchFile.read(1)[0]
                d.point((x,y), fill=color)

        image.convert("RGB").save("img1.jpg")

main()


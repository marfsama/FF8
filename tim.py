#!/usr/bin/env python3

from tools import *
from PIL import Image, ImageDraw

""" Size of chunk header
  4 bytes chunk size
  2 bytes x
  2 bytes y
  2 bytes w
  2 bytes h
-----
 12 bytes
"""
CHUNK_HEADER_SIZE = 12

class _BitPerPixel:
    def __init__(self, id, bpp, colorPaletSize):
        self.id = id
        self.bpp = bpp
        self.colorPaletSize = colorPaletSize

    def __str__(self):
        return "{name}: {{id: {id}, bpp: {bpp}, colorPaletSize: {colorPaletSize}}}".format(name=type(self).__name__, **vars(self))

def bitsPerPixel(id):
    return {
        0: _BitPerPixel(0, 4, 16),
        1: _BitPerPixel(1, 8, 256),
        2: _BitPerPixel(2, 16, 0),
        3: _BitPerPixel(3, 24, 0)
    }.get(id)

class TimFile:

    def __init__(self, bpp, palette, data):
        self.bpp = bpp
        self.palette = palette
        self.data = data

def readChunk(file):
    size = readu32(file)
    x,y,w,h = readu16(file),readu16(file),readu16(file),readu16(file)
    data = file.read(size - CHUNK_HEADER_SIZE)
    return x,y,w,h

def readImage(file):
    print("==== TIM Header ====")
    marker = readu32(file);
    if marker != 0x10:
        raise ValueError("unkown tim marker, should be 0x10, but is 0x{0:x}".format(marker))

    flags = readu32(file)
    """ Note: eventuell geben die Flags auch an, ob eine Palette und ein Bild folgt.
        Also: Bits 0-2 - BPP und damit, ob eine Palette folgt
              Bits 3 - Folgt ein Bild.
        Warum? Sowohl die Palette als auch das Bild ist in Chunks abgebildet, jeweils
               mit Size-Header vorne dran, um den ganzen Chunk einzulesen und/oder zu
               überspringen. Die Flags sind aber nicht Bestandteil eines Chunks. 
    """
    bpp = bitsPerPixel(flags & 3)
    hasPal = (flags >> 3) & 1
    palSize = readu32(file)
    palX = readu16(file)
    palY = readu16(file)
    palW = readu16(file)
    palH = readu16(file)

    print("flags:", flags, "{0:b}b".format(flags), "bpp:", bpp, "hasPal:", hasPal)
    printHex("palSize:", palSize)
    printHex("palX:", palX)
    printHex("palY:", palY)
    printHex("palW:", palW)
    printHex("palH:", palH)

    palette = []
    for i in range(bpp.colorPaletSize):
        r,g,b,a = fromPsColor(readu16(file))
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

    printHex("tell:", file.tell())

    imgSize = readu32(file)
    imgX = readu16(file)
    imgY = readu16(file)
    imgW = readu16(file)
    imgH = readu16(file)
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
            color = file.read(1)[0]
            d.point((x,y), fill=color)

    return image.convert("RGB")

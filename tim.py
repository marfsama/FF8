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

def _bitsPerPixel(id):
    return {
        0: _BitPerPixel(0, 4, 16),
        1: _BitPerPixel(1, 8, 256),
        2: _BitPerPixel(2, 16, 0),
        3: _BitPerPixel(3, 24, 0)
    }.get(id)

class TimFile:

    def __init__(self, bpp, palette, image):
        self.bpp = bpp
        self.palette = palette
        self.image = image

    def getPaletteImage(self):
        width, height = 256, 256

        image = Image.new("P", (width, height), 0)
        image.putpalette(self.palette)
        d = ImageDraw.ImageDraw(image)
        for x in range(width):
            for y in range(height):
                color = int(x / 16) * 16 + int(y / 16)
                d.point((x,y), fill=color)

        return image.convert("RGB")


def _readChunk(file):
    size = readu32(file)
    x,y,w,h = readu16(file),readu16(file),readu16(file),readu16(file)
    data = file.read(size - CHUNK_HEADER_SIZE)
    return x,y,w,h, data

def _readPalette(file, bpp):
    palX, palY, palW, palH, palData = _readChunk(file)

    palette = []
    for i in range(bpp.colorPaletSize):
        r,g,b,a = fromPsColor((palData[i*2+1] << 8) + palData[i*2])
        palette.append(r)
        palette.append(g)
        palette.append(b)
    return palette

def _readImage(file, bpp, palette):
    imgX, imgY, imgW, imgH, imgData = _readChunk(file)

    if (bpp.id == 0):
        imgW *= 4
    if (bpp.id == 1):
        imgW *= 2;

    image = Image.new("P", (imgW, imgH), 0)
    image.putpalette(palette)
    d = ImageDraw.ImageDraw(image)
    i = 0;
    for y in range(imgH):
        for x in range(imgW):
            color = imgData[i]
            d.point((x,y), fill=color)
            i = i + 1

    return image.convert("RGB")


def readTim(file):
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
    bpp = _bitsPerPixel(flags & 3)
    hasPal = (flags >> 3) & 1

    palette = _readPalette(file, bpp)
    image = _readImage(file, bpp, palette)

    return TimFile(bpp, palette, image)


def readTimFile(fileName):
    with open(fileName, "rb") as file:
        return readTim(file)



from tools import *

class Model:
    def __str__(self):
        return "Model with\n\t{0} vertices".format(len(self.vertices))

class FaceData:
    def __init__(self, mchFile, index):
        """ 
            Der untere Teil des Value1 geht bis 0x18 (24). Das entspricht der 0-basierten
            Indizierung dieses Arrays. Könnte das ein "Next" Pointer oder so sein?
            Oder wird damit ein Triangle Strip gebildet und eine negative Zahl gibt das 
            Ende an? Eher unwahrscheinlich, da die indizes nicht alle Vertices abgraben
            Könnte hiermit ein skelet angegeben werden? DAnn ist das ein prev. Pointer und
            value 3 ein drehwert und/oder ein anderer constraint Zahl 
        """
        self.index = index
        self.value1 = readu16(mchFile)
        # always 0x40 * value1. As one entry in this list ix 0x40 bytes, this is a byte offset into this list. 
        self.offset = readu16(mchFile)
        # always 0
        self.zero = readu32(mchFile)
        self.value3 = read16(mchFile)
        self.zero2 = read16(mchFile)
        # always 0
        self.unknown = readlist(readu32, mchFile, 13)

        # some sanity checks
        if self.value1 > self.index:
            raise ValueError("value1 must not be greater than the item index. index: "+str(self.index)+" actual: "+str(self.value1))
        if self.offset != self.value1 * 64:
            raise ValueError("offset must be value1 * 0x40. expected: "+str(self.value1 * 64)+" actual: "+str(self.offset))
        if self.zero != 0:
            raise ValueError("zero sould be 0. actual: "+str(self.zero))
        if self.value3 > 0:
            raise ValueError("value3 sould always be < 0. actual: "+str(self.value3))

        for value in self.unknown:
            if value != 0:
                raise ValueError("unknown array sould only contains zeros. actual: "+str(self.unknown))


    def __str__(self):
        return "Face: {0}, offset: {1}, {2}".format(self.value1, self.offset, self.value3)

class Vertex:
    def __init__(self, values):
        self.x = values[0]
        self.y = values[1]
        self.z = values[2]
        self.w = values[3]

        if self.w != 0:
            raise ValueError("w sould always be 0. actual: "+str(self.w))

    def __str__(self):
        return "Vertex: x: {0} y: {1} z: {2} w: {3}".format(self.x, self.y, self.z, self.w)

class FaceSpan:
    """
        word - Description
          0  - start index: index into vertex array (list2). beginning from 0
          1  - length: this value plus the start index is the next rows start index
          2  - unknown: some small value. max encountered value is 0x3a, never zero. maybe some kind of flags?
          3  - zero: always zero

        this is maybe some kind of polygon span 
    """
    def __init__(self, values):
        self.startIndex = values[0]
        self.length = values[1]
        self.unknown = values[2]
        self.zero = values[3]

    def __str__(self):
        return "FaceSpan: startIndex: {0} length: {1} unknown {2:b}".format(self.startIndex, self.length, self.unknown)

class Entry4:
    def __init__(self, mchFile):
        # entweder 0x607 oder 0x709. Bitfield?
        value1 = readu16(mchFile)
        # entweder 0x2501 oder 0x2d01
        value2 = readu16(mchFile)
        # konstant 0x44
        value3 = readu32(mchFile)
        # konstant 0x01
        value4 = readu32(mchFile)
        # 8 x index into vertex array
        value5 = readu16(mchFile)
        value6 = readu16(mchFile)
        value7 = readu16(mchFile)
        value8 = readu16(mchFile)
        value9 = readu16(mchFile)
        value10 = readu16(mchFile)
        value11 = readu16(mchFile)
        value12 = readu16(mchFile)
        # 4 x konstant 0x7f7f7f7f oder 0xffffffff (auch das könnten 8x uint16 sein)
        const1 = readu32(mchFile)
        const2 = readu32(mchFile)
        const3 = readu32(mchFile)
        const4 = readu32(mchFile)
        # 8x releativ kleine byte-zahlen. meistens ist das 7. Bit (LSB) nicht gesetzt.
        # könnten das bone weights sein?
        valuebytes = mchFile.read(8);
        # immer 0x0
        zero1 = readu16(mchFile)
        # entweder 0, 1 oder 2
        value13 = readu16(mchFile)
        # 4 x immer 0x0 (oder auch 8 x 0x0 als byte)
        zeroes = readlist(readu16,mchFile, 4)


def readList1(mchFile, modelOffset, numEntries):
    print("entries1 - size: 64 bytes -", numEntries, "entries - skeleton?")
    faces = []
    for i in range(numEntries):
        face = FaceData(mchFile, i)
        faces.append(face)
    return faces

def readVertices(mchFile, modelOffset, numEntries):
    print("entries2 - size: 8 bytes -", numEntries, " entries - vertices? x,y,z,w?")

    vertices = []
    for i in range(numEntries):
        values = readlist(read16, mchFile, 4)
        vertices.append(Vertex(values))
    return vertices


def readList3(mchFile, modelOffset, numEntries):
    """
        seems to be always 20 entries
    """
    print("entries3 - size: 1 byte -",numEntries,"entries - irgendein bitmask zeugs? animations?")

    entries3 = []
    for i in range(numEntries):
        entries3.append(readu8(mchFile))
    #print("0: {0}".format(entries3))
    return entries3

def readList4(mchFile, modelOffset, numEntries):
    print("entries4 - size: 64 bytes -", numEntries,"entries - bone data?")

    entries4 = []
    for i in range(numEntries):
        entries4.append(Entry4(mchFile))
    return entries4

def readList5(mchFile, modelOffset, numEntries):
    """
        this list contains only one entry in all encountered models 
    """
    print("entries5 - size: 32 bytes -", numEntries,"entries")

    # sparse data, only entry 1, 9 & 11 (zero based) contains data
    for i in range(numEntries):
        stuff = readlist(readu16,mchFile, 16)
        # printHexListMultiLine(str(i+1)+" stuff", stuff)

def readFaceSpans(mchFile, modelOffset, numEntries):
    """
        word - Description
          0  - start index: index into vertex array (list2). beginning from 0
          1  - length: this value plus the start index is the next rows start index
          2  - unknown: some small value. max encountered value is 0x3a, never zero
          3  - zero: always zero

        this is maybe some kind of polygon span 
    """
    print("entries6 - size: 8 bytes -", numEntries, "entries triangle span")

    faceSpans = []
    for i in range(numEntries):
        values = readlist(readu16,mchFile, 4)
        faceSpans.append(FaceSpan(values))
    return faceSpans

def readList7(mchFile, modelOffset, numEntries):
    """
        unknown. never encountered entries in this list.
    """
    print("entries7 - size: ?? bytes -", numEntries,"entries")
#    printHex("tell", mchFile.tell())
#    printHex("tell", mchFile.tell() - modelOffset)

def readModel(mchFile):
    model = Model()
    model.modelOffset = mchFile.tell();
    model.numEntries = readlist(readu32, mchFile, 7)

    model.temp1 = readu16(mchFile)
    model.temp2 = readu16(mchFile)
    printHex("temp1", model.temp1)
    printHex("temp2", model.temp2)

    listoffsets = readlist(readu32, mchFile, 7)

    model.stuff = []
    for s in range(2):
        value = readu16(mchFile)
        model.stuff.append(value)
        printHex(str(s+1), value)

    model.faces = readList1(mchFile, model.modelOffset, model.numEntries[0])
    model.vertices = readVertices(mchFile, model.modelOffset, model.numEntries[1])
    model.entries3 = readList3(mchFile, model.modelOffset, model.numEntries[2])
    model.entries4 = readList4(mchFile, model.modelOffset, model.numEntries[3])
    readList5(mchFile, model.modelOffset, model.numEntries[4])
    model.faceSpans = readFaceSpans(mchFile, model.modelOffset, model.numEntries[5])
    readList7(mchFile, model.modelOffset, model.numEntries[6])

    return model


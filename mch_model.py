from tools import *

class Model:
    def __str__(self):
        return "Model with\n\t{0} vertices".format(len(self.vertices))

class Bone:
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
        # parent
        self.parent = readu16(mchFile)
        # always 0x40 * value1. As one entry in this list ix 0x40 bytes, this is a byte offset into this list. 
        self.offset = readu16(mchFile)
        # always 0
        self.zero = readu32(mchFile)
        # bone length
        self.length = read16(mchFile)
        self.zero2 = read16(mchFile)
        # always 0
        self.zero3 = readlist(readu32, mchFile, 13)

    def __str__(self):
        return "parent bone: {0}, parent offset: {1}, bone length: {2}".format(self.parent, self.offset, self.length)

class Vertex:
    def __init__(self, mchFile):
        self.x = read16(mchFile)
        self.y = read16(mchFile)
        self.z = read16(mchFile)
        self.w = read16(mchFile)

        if self.w != 0:
            raise ValueError("w sould always be 0. actual: "+str(self.w))

    def __str__(self):
        return "Vertex: x: {0} y: {1} z: {2} w: {3}".format(self.x, self.y, self.z, self.w)

class Limb:
    def __init__(self, values):
        self.startVertexId = values[0]
        self.numVertices = values[1]
        self.boneId = values[2]
        self.zero = values[3]

    def __str__(self):
        return "Limb: startVertexId: {0} numVertices: {1} boneId: {2}".format(self.startVertexId, self.numVertices, self.boneId)

class TextureCoord:

    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return "{0:.2f}/{1:.2f}".format(self.u, self.v)

def readUV(mchFile):
    coord = TextureCoord()
    coord.u = read8(mchFile) / 127.0
    coord.v = read8(mchFile) / 127.0
    return coord


class Face:
    def __init__(self, mchFile):
        # GPU command
        self.value1 = readu16(mchFile)
        # GPU command to render triangle or quad (0x2501, 0x2d01). 
        #  0x25 - 3 vertex polygon, no brightness calculation
        #  0x2d - 4 vertex polygon, no brightness calculation
        #  0x01 - clear cache
        self.value2 = readu16(mchFile)
        # konstant 0x44
        self.value3 = readu32(mchFile)
        # konstant 0x01
        self.value4 = readu32(mchFile)
        self.vertexIndices = readlist(readu16,mchFile, 4)
        self.normalIndices = readlist(readu16,mchFile, 4)
        # 4 x konstant 0x7f7f7f7f oder 0xffffffff (auch das könnten 8x uint16 sein)
        # might be vertex color
        self.const1 = readu32(mchFile)
        self.const2 = readu32(mchFile)
        self.const3 = readu32(mchFile)
        self.const4 = readu32(mchFile)
        # 8x releativ kleine byte-zahlen. meistens ist das 7. Bit (LSB) nicht gesetzt.
        # uv koordinaten
        self.textureCoords = readlist(readUV,mchFile, 4);
        # immer 0x0
        self.zero1 = readu16(mchFile)
        # entweder 0, 1 oder 2
        self.textureId = readu16(mchFile)
        # 4 x immer 0x0 (oder auch 8 x 0x0 als byte)
        self.zeroes = readlist(readu16,mchFile, 4)

        # some sanity checks
        if self.value1 != 0x607 and self.value1 != 0x709:
            raise ValueError("value1 must be either 0x607 or 0x709. actual: {0:x}".format(self.value1))
        if self.value2 != 0x2501 and self.value2 != 0x2d01:
            raise ValueError("value2 must be either 0x2501 or 0x2d01. actual: {0:x}".format(self.value2))
        if self.value3 != 0x44:
            raise ValueError("value3 must be 0x44. actual: {0:x}".format(self.value3))
        if self.value4 != 0x1:
            raise ValueError("value3 must be 0x1. actual: {0:x}".format(self.value4))
        if self.const1 != 0x7f7f7f and self.const1 != 0xffffff and self.const1 != 0:
            raise ValueError("const1 must be 0x7f7f7f. actual: {0:x}".format(self.const1))
        if self.const2 != 0x7f7f7f and self.const2 != 0xffffff and self.const2 != 0:
            raise ValueError("const2 must be 0x7f7f7f. actual: {0:x}".format(self.const2))
        if self.const3 != 0x7f7f7f and self.const3 != 0xffffff and self.const3 != 0:
            raise ValueError("const3 must be 0x7f7f7f. actual: {0:x}".format(self.const3))
        if self.const4 != 0x7f7f7f and self.const4 != 0xffffff and self.const4 != 0:
            raise ValueError("const4 must be 0x7f7f7f. actual: {0:x}".format(self.const4))

def readBones(mchFile, modelOffset, numEntries):
    print("entries1 - size: 64 bytes -", numEntries, "entries - bones")
    bones = []
    for i in range(numEntries):
        bone = Bone(mchFile, i)
        bones.append(bone)
    return bones

def readVertices(mchFile, modelOffset, numEntries):
    print("entries2 - size: 8 bytes -", numEntries, " entries - vertices? x,y,z,w?")

    vertices = []
    for i in range(numEntries):
        vertices.append(Vertex(mchFile))
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

def readFaces(mchFile, modelOffset, numEntries):
    print("entries4 - size: 64 bytes -", numEntries,"entries - face data (triangle/quad)")

    faces = []
    for i in range(numEntries):
        faces.append(Face(mchFile))
    return faces

def readList5(mchFile, modelOffset, numEntries):
    """
        this list contains only one entry in all encountered models 
    """
    print("entries5 - size: 32 bytes -", numEntries,"entries")

    # sparse data, only entry 1, 9 & 11 (zero based) contains data
    for i in range(numEntries):
        stuff = readlist(readu16,mchFile, 16)
#        print(str(i)+" stuff ", *stuff)

def readLimbs(mchFile, modelOffset, numEntries):
    """
        word - Description
          0  - start vertex index
          1  - length: number of vertices
          2  - bone id
          3  - zero: always zero
    """
    print("entries6 - size: 8 bytes -", numEntries, "entries - limbs")

    limbs = []
    for i in range(numEntries):
        values = readlist(readu16,mchFile, 4)
        limbs.append(Limb(values))
    return limbs

def readList7(mchFile, modelOffset, numEntries):
    """
        unknown. never encountered entries in this list.
    """
    print("entries7 - size: ?? bytes -", numEntries,"entries")

def readModel(mchFile):
    model = Model()
    model.modelOffset = mchFile.tell();
    model.numEntries = readlist(readu32, mchFile, 7)

    model.numTriangles = readu16(mchFile)
    model.numQuads = readu16(mchFile)
    printHex("numTriangles", model.numTriangles)
    printHex("numQuads", model.numQuads)

    listoffsets = readlist(readu32, mchFile, 7)

    model.temp3 = readu16(mchFile)
    model.temp4 = readu16(mchFile)
    printHex("temp3", model.temp3)
    printHex("temp4", model.temp4)

    model.bones = readBones(mchFile, model.modelOffset, model.numEntries[0])
    model.vertices = readVertices(mchFile, model.modelOffset, model.numEntries[1])
    model.entries3 = readList3(mchFile, model.modelOffset, model.numEntries[2])
    model.faces = readFaces(mchFile, model.modelOffset, model.numEntries[3])
    model.entries5 = readList5(mchFile, model.modelOffset, model.numEntries[4])
    model.limbs = readLimbs(mchFile, model.modelOffset, model.numEntries[5])
    readList7(mchFile, model.modelOffset, model.numEntries[6])

    return model


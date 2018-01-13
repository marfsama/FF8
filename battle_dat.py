#!/usr/bin/env python3

from tools import *
from export import *

import os
import sys

class Bone:
    pass

class Mesh:
    def __init__(self):
        self.triangles = []
        self.quads = []
        self.subMeshes = []


class SubMesh:
    def __init__(self, boneId, vertices):
        self.boneId = boneId
        self.vertices = vertices

    def __str__(self):
        return("    boneid: {0}, vertices: {1}".format(self.boneId, self.vertices))




class Polygon:
    def __init__(self, vertexIndices, uv, unk):
        self.vertexIndices = vertexIndices
        self.uv = uv
        self.unk = unk

    def __str__(self):
        type = "tris"
        if len(self.vertexIndices) == 4:
            type = "quad"
        return "{0}: vertices {1}, uvs: {2}, unknown: {3}".format(type, self.vertexIndices, self.uv, toHex(self.unk))


def readBones(file, offset):
    file.seek(offset)
    numBones = readu16(file)
    print ("numBones:", numBones)
    unknown = readlist(readu16, file, 7)
    print("unknowns:", unknown)
    print("tell: 0x{0:x}".format(file.tell()))

    bones = []
    for i in range(numBones):
        bone = Bone()
        bone.parent = read16(file)
        bone.length = -read16(file)
        bone.unknown = readlist(readu16, file, 22)
        bones.append(bone)
        print("{0}. bone, parent: {1}, length: {2}".format(i, bone.parent, bone.length))

    return bones

def readVertex(file):
    return (read16(file),read16(file),read16(file))

def readUV(file):
    return (readu8(file),readu8(file))


def readMeshes(file, geometryOffset):
    file.seek(geometryOffset)
    numGroups = readu32(file)
    groupOffsets = readlist(readu32, file, numGroups)
    print("num: {0} offsets: {1}".format(numGroups, toHex(groupOffsets)))

    meshes = []
    for index, groupOffset in enumerate(groupOffsets):
        mesh = Mesh()
        meshes.append(mesh)
        file.seek(geometryOffset + groupOffset)
        numBones = readu16(file)
        print("group {0} @ 0x{1:x}".format(index, groupOffset))
        print("  numBones: {0}".format(numBones))
        for boneNum in range(numBones):
            boneId = readu16(file)
            numVertices = readu16(file)
            vertices = readlist(readVertex, file, numVertices)
            subMesh = SubMesh(boneId, vertices)
            mesh.subMeshes.append(subMesh)
            print("  bone: {0}".format(boneNum))
            print(str(subMesh))
            #print("    vertices: {0}".format(vertices))


        # skip to dword boundary
        filePos = (file.tell() + 3) & 0xFFFFFFFC
        file.seek(filePos)

        numTriangles = readu16(file)    
        numQuads = readu16(file)
        # skip 8 bytes, these are always 0
        readu32(file)
        readu32(file)
        for trisNum in range(numTriangles):
            vertexIndices = readlist(readu16, file, 3)
            vertexIndices[0] = vertexIndices[0] & 0x7fff
            uv = readlist(readUV, file, 2)
            unk = readlist(readu16, file, 1)
            uv.append(readUV(file))
            unk.append(readu16(file))
            polygon = Polygon(vertexIndices, uv, unk)
            print(str(polygon))
            mesh.triangles.append(polygon)

        for quadNum in range(numQuads):
            vertexIndices = readlist(readu16, file, 4)
            vertexIndices[0] = vertexIndices[0] & 0x7fff
            uv = readlist(readUV, file, 1)
            unk = readlist(readu16, file, 1)
            uv.append(readUV(file))
            unk.append(readu16(file))
            uv.extend(readlist(readUV, file, 2))
            polygon = Polygon(vertexIndices, uv, unk)
            print(str(polygon))
            mesh.triangles.append(polygon)
    # unknown. base rotation?    
    readu32(file)
    return meshes

def readTextures(file, textureListOffset):
    file.seek(textureListOffset)

    numTextures = readu32(file)

    textures = {}

    textureOffsets = readlist(readu32, file, numTextures)
    for index, relativeoffset in enumerate(textureOffsets):
        absoluteOffset = textureListOffset + relativeoffset
        file.seek(absoluteOffset)
        tim = readTim(file)

        textures[index] = tim.image

    return textures

def readAnimations(file, animationSectionOffset):
    file.seek(animationSectionOffset)

    numAnimations = readu32(file)
    animationOffsets = readlist(readu32, file, numAnimations)

    print("{0} animations: {1}".format(numAnimations, animationOffsets))

    for index, relativeoffset in enumerate(animationOffsets):
        absoluteOffset = animationSectionOffset + relativeoffset
        file.seek(absoluteOffset)
        values = readlist(readu32, file, 10)
        print(index, toHex(values))


def main():
    fileName = sys.argv[1]
    print(fileName)
    length = os.stat(fileName).st_size

    with open(fileName, "rb") as file:
        numEntries = readu32(file)
        print("numentries:", numEntries)

        offsetList = readlist(readu32, file, numEntries+1)
        offsets = Offsets(["Skeleton","Geometry","Animation","Unknown1","Unknown2","Unknown3","MonsterInfo","BattleScript","Sound data1","Sound data2","Texture", "FileLength"])
        offsets.setOffsets(offsetList)

        print(str(offsets))

        print("tell: 0x{0:x}".format(file.tell()))

        bones = readBones(file, offsets.getOffset("Skeleton"))
#        meshes = readMeshes(file, offsets.getOffset("Geometry"))
#        textures = readTextures(file, offsets.getOffset("Texture"))

        readAnimations(file, offsets.getOffset("Animation"))
        print("tell: 0x{0:x}".format(file.tell()))


        print("file length: 0x{0:x}".format(length))
        print("last entry: 0x{0:x}".format(offsets.getOffset("FileLength")))
        

main()


#!/usr/bin/env python3

from tools import *
from mch_model import *
from export import *

#from functools import partial
import os
import sys


basePath = "main_chr/"


def readHeader(file):
    """ header lesen """
    offsets = []
    for i in range(8):
        offsets.append(readu32(file))

    """ die ZAhl im oberen word des offsets könnte die Textur-Nummer oder texture unit sein.
    """

    return offsets

def findModelOffset(offsets):
    found = False
    for offset in offsets:
        if found:
            return offset
        if offset == 0xffffffff:
            found = True
    return -1


def statisticsBones(model):
    for index, face in enumerate(model.faces):
        print(index+1, ":", str(face))

def statisticsVertexList(model):
    minMaxX = MinMax()
    minMaxY = MinMax()
    minMaxZ = MinMax()

    for index, vertex in enumerate(model.vertices):
        print(index, ":", str(vertex))
        minMaxX.add(vertex.x)
        minMaxY.add(vertex.y)
        minMaxZ.add(vertex.z)
    print("x: ", minMaxX)
    print("y: ", minMaxY)
    print("z: ", minMaxZ)

def statisticsList3(model):
    minValue, maxValue, sumValue = 1000, -1000, 0
    for index, entry in enumerate(model.entries3):
        print("{0:3}: dec: {1:3} hex: {1:3x} bin: {1:8b}".format(index, entry))
        minValue = min(minValue, entry)
        maxValue = max(maxValue, entry)
        sumValue += entry
    print("    value min:",minValue," max:", maxValue,"sum:",sumValue)

def statisticsFaces(model):
    maxIndex = 0;
    for index, face in enumerate(model.faces):
        for vertexIndex in face.vertexIndices:
            maxIndex = max(maxIndex, vertexIndex)
        print("{0}, {1:x}, vertexIDs: {2}, normals: {3} uv: {4} texture: {5}".format(index, face.value1, face.vertexIndices, face.normalIndices, str(face.textureCoords), face.textureId))
    print("maxIndex ", maxIndex)

def statisticsLimbs(model):
    for index, limb in enumerate(model.limbs):
        print("{0}, {1}".format(index, str(limb)))

def xyvertex(vertex):
    return (vertex.x, vertex.y)

def xzvertex(vertex):
    return (vertex.x, vertex.z)

def yzvertex(vertex):
    return (vertex.y, vertex.z)

def plotVertices(model, function, fileName):
    """
        Usage:
            plotVertices(model, xyvertex, fileName+".xy.jpg")
            plotVertices(model, xzvertex, fileName+".xz.jpg")
            plotVertices(model, yzvertex, fileName+".yz.jpg")

    """
    vertexImage = VertexImage()
    for i in range(len(model.vertices)):
        vertex = model.vertices[i]
        vertexImage.addVertex(*function(vertex))

    vertexImage.saveImage(fileName)

def plotTextureFace(draw, face, vertices):
    p1 = face.textureCoords[0].u * 512, face.textureCoords[0].v * 512
    p2 = face.textureCoords[1].u * 512, face.textureCoords[1].v * 512
    p3 = face.textureCoords[2].u * 512, face.textureCoords[2].v * 512
    p4 = face.textureCoords[3].u * 512, face.textureCoords[3].v * 512
    boneId = vertices[face.vertexIndices[0]].boneId
    color = COLORS[boneId % len(COLORS)]
    if face.value1 == 0x607:
        draw.line(p1 + p2, fill=color)
        draw.line(p2 + p3, fill=color)
        draw.line(p1 + p3, fill=color)
    else:
        draw.line(p1 + p2, fill=color)
        draw.line(p2 + p4, fill=color)
        draw.line(p3 + p4, fill=color)
        draw.line(p3 + p1, fill=color)


def plotTextureMesh(model, textures, fileName):
    for limb in model.limbs:
        for relativeVertexId in range(limb.numVertices):
            vertexId = limb.startVertexId + relativeVertexId
            vertex = model.vertices[vertexId]
            vertex.boneId = limb.boneId

    for textureId in textures:
        image = textures[textureId].resize((512, 512))
        draw = ImageDraw.ImageDraw(image)
        for face in model.faces:
            if face.textureId == textureId:
                plotTextureFace(draw, face, model.vertices)
        image.save(fileName+".texmesh"+str(textureId)+".jpg")


def exportMesh(model, length, fileName):
#    statisticsBones(model)
#    statisticsVertexList(model)
#    statisticsList3(model)
#    statisticsFaces(model)
    statisticsLimbs(model),
#    plotVertices(model, xyvertex, fileName+".xy.jpg")
#    plotVertices(model, xzvertex, fileName+".xz.jpg")
#    plotVertices(model, yzvertex, fileName+".yz.jpg")

    with open(fileName+".obj", "w") as objFile:
        objFile.write("mtllib "+fileName+".mtl\n")
        outputVertexList(objFile, model)
        outputFaces(objFile, model)



def main():
    fileName = sys.argv[1]
    print(fileName)
    length = os.stat(basePath + fileName).st_size
    textures = {}
    with open(basePath + fileName, "rb") as mchFile:
        offsets = readHeader(mchFile)

        for offset in offsets:
            if offset == 0xffffffff:
                break 
            timOffset = offset & 0x0fffffff
            textureNr = offset >> 28
            mchFile.seek(timOffset)
            texture = readTim(mchFile)
            textures[textureNr] = texture.image

        modelOffset = findModelOffset(offsets)
        mchFile.seek(modelOffset)
        model = readModel(mchFile)
        print("end of file")
        printHex("tell", mchFile.tell())
        printHex("remaining", length - mchFile.tell())

        saveTextures(textures, fileName)
        createMaterial(textures, fileName)
        exportMesh(model, length, fileName)
        plotTextureMesh(model, textures, fileName)


main()


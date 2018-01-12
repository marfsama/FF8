
from PIL import Image, ImageDraw
from tim import *

COLORS = [
    "#e6194b",
    "#3cb44b",
    "#ffe119",
    "#0082c8",
    "#f58231",
    "#911eb4",
    "#46f0f0",
    "#f032e6",
    "#d2f53c",
    "#fabebe",
    "#008080",
    "#e6beff",
    "#aa6e28",
    "#fffac8",
    "#800000",
    "#aaffc3",
    "#808000",
    "#ffd8b1",
    "#000080",
    "#808080",
    "#FFFFFF",
    "#000000"
]

def saveTextures(textures, fileName):
    for textureId in textures:
        image = textures[textureId]
        image.save(fileName+".tim."+str(textureId)+".jpg")

def createMaterial(textures, fileName):
    with open(fileName+".mtl", "w") as mtlFile:
        for textureId in textures:
            name = fileName+".tim."+str(textureId)+".jpg"
            mtlFile.write("newmtl mat{0}\n".format(textureId))
            mtlFile.write("map_Kd {0}\n".format(name))
            mtlFile.write("\n")


def outputVertexList(objFile, model):
    for i in range(len(model.vertices)):
        vertex = model.vertices[i]
        outputVertex(objFile, vertex)

def outputVertex(objFile, vertex):
    objFile.write("v {0} {1} {2}\n".format(vertex.x, vertex.y, vertex.z))

def outputPoint(objFile, vertexIndex):
    objFile.write("p {0}\n".format(vertexIndex+1))

def outputLine(objFile, vertexIndexFrom, vertexIndexTo):
    objFile.write("l {0} {1}\n".format(vertexIndexFrom+1,vertexIndexTo+1))

def outputFaces(objFile, model):
    vertexTextureIndex = 1
    for i in range(len(model.faces)):
        entry = model.faces[i]
        objFile.write("vt {0} {1}\n".format(entry.textureCoords[0].u, entry.textureCoords[0].v))
        objFile.write("vt {0} {1}\n".format(entry.textureCoords[1].u, entry.textureCoords[1].v))
        objFile.write("vt {0} {1}\n".format(entry.textureCoords[2].u, entry.textureCoords[2].v))
        objFile.write("vt {0} {1}\n".format(entry.textureCoords[3].u, entry.textureCoords[3].v))

        objFile.write("usemtl mat{0}\n".format(entry.textureId))
        if entry.value1 == 0x607:
            objFile.write("f ")
            objFile.write("{0}/{1} ".format(entry.vertexIndices[0]+1, vertexTextureIndex))
            objFile.write("{0}/{1} ".format(entry.vertexIndices[1]+1, vertexTextureIndex+1))
            objFile.write("{0}/{1} ".format(entry.vertexIndices[2]+1, vertexTextureIndex+2))
            objFile.write("\n")

        if entry.value1 == 0x709:
            objFile.write("f ")
            objFile.write("{0}/{1} ".format(entry.vertexIndices[0]+1, vertexTextureIndex))
            objFile.write("{0}/{1} ".format(entry.vertexIndices[1]+1, vertexTextureIndex+1))
            objFile.write("{0}/{1} ".format(entry.vertexIndices[3]+1, vertexTextureIndex+3))
            objFile.write("{0}/{1} ".format(entry.vertexIndices[2]+1, vertexTextureIndex+2))
            objFile.write("\n")

        vertexTextureIndex += 4

class VertexImage:

    def __init__(self):
        self.minMaxX = MinMax()
        self.minMaxY = MinMax()
        self.vertices = []

    def addVertex(self, x, y):
        self.vertices.append( (x,y) )
        self.minMaxX.add(x)
        self.minMaxY.add(y)


    def saveImage(self, fileName):
        IMAGE_SIZE = 512
        xscale = self.minMaxX.max - self.minMaxX.min
        yscale = self.minMaxY.max - self.minMaxY.min
        image = Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE))
        d = ImageDraw.ImageDraw(image)

        for x,y in self.vertices:
            normalizedX = (x - self.minMaxX.min) / xscale
            normalizedY = (y - self.minMaxY.min) / yscale
            xpos = normalizedX*IMAGE_SIZE
            ypos = normalizedY*IMAGE_SIZE
            d.point((xpos, ypos), fill="#FFFFFF")

        image.save(fileName)

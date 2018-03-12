#!/usr/bin/env python3

from mch_model import *
from export import *

# from functools import partial
import os
import sys


basePath = "main_chr/"


def read_header(file):
    """ header lesen """
    offsets = []
    for i in range(8):
        offsets.append(readu32(file))

    """ die Zahl im oberen word des offsets ist die texture-id
    """

    return offsets


def find_model_offset(offsets):
    found = False
    for offset in offsets:
        if found:
            return offset
        if offset == 0xffffffff:
            found = True
    return -1


def statistics_bones(model):
    for index, face in enumerate(model.faces):
        print(index+1, ":", str(face))


def statistics_vertex_list(model):
    min_max_x = MinMax()
    min_max_y = MinMax()
    min_max_z = MinMax()

    for index, vertex in enumerate(model.vertices):
        print(index, ":", str(vertex))
        min_max_x.add(vertex.x)
        min_max_y.add(vertex.y)
        min_max_z.add(vertex.z)
    print("x: ", min_max_x)
    print("y: ", min_max_y)
    print("z: ", min_max_z)


def statistics_list3(model):
    min_value, max_value, sum_value = 1000, -1000, 0
    for index, entry in enumerate(model.entries3):
        print("{0:3}: dec: {1:3} hex: {1:3x} bin: {1:8b}".format(index, entry))
        min_value = min(min_value, entry)
        max_value = max(max_value, entry)
        sum_value += entry
    print("    value min:",min_value," max:", max_value,"sum:",sum_value)


def statistics_faces(model):
    max_index = 0
    for index, face in enumerate(model.faces):
        for vertexIndex in face.vertexIndices:
            max_index = max(max_index, vertexIndex)
        print("{0}, {1:x}, vertexIDs: {2}, normals: {3} uv: {4} texture: {5}".format(index, face.value1, face.vertexIndices, face.normalIndices, str(face.textureCoords), face.textureId))
    print("max_index ", max_index)


def statistics_limbs(model):
    for index, limb in enumerate(model.limbs):
        print("{0}, {1}".format(index, str(limb)))


def xy_vertex(vertex):
    return vertex.x, vertex.y


def xz_vertex(vertex):
    return vertex.x, vertex.z


def yz_vertex(vertex):
    return vertex.y, vertex.z


def plot_vertices(vertices, function, filename):
    """
        Usage:
            plotVertices(model.vertices, xyvertex, fileName+".xy.jpg")
            plotVertices(model.vertices, xzvertex, fileName+".xz.jpg")
            plotVertices(model.vertices, yzvertex, fileName+".yz.jpg")

    """
    vertex_image = VertexImage()
    for vertex in vertices:
        vertex_image.addVertex(*function(vertex))

    vertex_image.saveImage(filename)


def plot_texture_face(draw, face, vertices):
    p1 = face.textureCoords[0].u * 512, face.textureCoords[0].v * 512
    p2 = face.textureCoords[1].u * 512, face.textureCoords[1].v * 512
    p3 = face.textureCoords[2].u * 512, face.textureCoords[2].v * 512
    p4 = face.textureCoords[3].u * 512, face.textureCoords[3].v * 512
    bone_id = vertices[face.vertexIndices[0]].boneId
    color = COLORS[bone_id % len(COLORS)]
    if face.value1 == 0x607:
        draw.line(p1 + p2, fill=color)
        draw.line(p2 + p3, fill=color)
        draw.line(p1 + p3, fill=color)
    else:
        draw.line(p1 + p2, fill=color)
        draw.line(p2 + p4, fill=color)
        draw.line(p3 + p4, fill=color)
        draw.line(p3 + p1, fill=color)


def plot_texture_mesh(model, textures, filename):
    for textureId in textures:
        image = textures[textureId].resize((512, 512))
        draw = ImageDraw.ImageDraw(image)
        for face in model.faces:
            if face.textureId == textureId:
                plot_texture_face(draw, face, model.vertices)
        image.save(filename+".texmesh"+str(textureId)+".jpg")


def export_mesh(model, length, filename):
    #    statisticsBones(model)
    #    statisticsVertexList(model)
    #    statisticsList3(model)
    #    statisticsFaces(model)
    #    statisticsLimbs(model)

    for limb in model.limbs:
        vertices = model.vertices[limb.startVertexId:limb.startVertexId+limb.numVertices]
        plot_vertices(vertices, xy_vertex, filename+"."+str(limb.boneId)+".xy.jpg")
        plot_vertices(vertices, xz_vertex, filename+"."+str(limb.boneId)+".xz.jpg")
        plot_vertices(vertices, yz_vertex, filename+"."+str(limb.boneId)+".yz.jpg")

    with open(filename+".obj", "w") as objFile:
        objFile.write("mtllib "+filename+".mtl\n")
        outputVertexList(objFile, model)
        outputFaces(objFile, model)


def main():
    filename = sys.argv[1]
    print(filename)
    length = os.stat(basePath + filename).st_size
    textures = {}
    with open(basePath + filename, "rb") as mchFile:
        offsets = read_header(mchFile)

        for offset in offsets:
            if offset == 0xffffffff:
                break 
            tim_offset = offset & 0x0fffffff
            texture_nr = offset >> 28
            mchFile.seek(tim_offset)
            texture = readTim(mchFile)
            textures[texture_nr] = texture.image

        model_offset = find_model_offset(offsets)
        mchFile.seek(model_offset)
        model = readModel(mchFile)
        print("end of file")
        printHex("tell", mchFile.tell())
        printHex("remaining", length - mchFile.tell())

        saveTextures(textures, filename)
        createMaterial(textures, filename)
        export_mesh(model, length, filename)
        plot_texture_mesh(model, textures, filename)


main()


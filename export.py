def outputVertexList(objFile, model):
    for vertex in model.vertices:
        outputVertex(objFile, vertex)

def outputVertex(objFile, vertex):
    objFile.write("v {0} {1} {2}\n".format(vertex.x, vertex.y, vertex.z))

def outputPoint(objFile, vertexIndex):
    objFile.write("p {0}\n".format(vertexIndex+1))

def outputLine(objFile, vertexIndexFrom, vertexIndexTo):
    objFile.write("l {0} {1}\n".format(vertexIndexFrom+1,vertexIndexTo+1))

def outputFaceSpan(objFile, model, faceSpan):
    for vertexIndex in range(faceSpan.length):
        outputPoint(objFile, vertexIndex)

    #for vertexIndex in range(faceSpan.length-1):
    #    outputLine(objFile, faceSpan.startIndex + vertexIndex, faceSpan.startIndex + vertexIndex + 1)


#    objFile.write("l ")
#    for vertexIndex in range(faceSpan.length):
#        objFile.write("\n")
#    objFile.write("\n")

